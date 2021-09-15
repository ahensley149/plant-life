from flask import jsonify, request
from flask_cors import CORS
from models import *
from datetime import datetime, date, timedelta

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/enviros')
def list_environments():
    """Index of all environments for updating and deleting"""
    enviros = {}
    enviro_names = Enviro.query.with_entities(Enviro.id, Enviro.name).all()
    enviro = Enviro.query.get_or_404(1)
    for env in enviro_names:
        enviros[env.id] = env.name
    return jsonify({ 'enviros': enviros,
        'enviro': [enviro.to_dict()]})

@app.route('/update_climate/<int:id>', methods=['POST'])
def update_climate(id):
    """Updates the min and max settings for air temp and humidity of the environment"""
    if request.method == 'POST':
        post_data = request.get_json()
        enviro = Enviro.query.get_or_404(id)

        enviro.min_temp = post_data['min_temp']
        enviro.max_temp = post_data['max_temp']
        enviro.min_humid = post_data['min_humid']
        enviro.max_humid = post_data['max_humid']

        try:
            db.session.commit()
        except:
            return 'There was an issue updating the climate controls'

@app.route('/equip_log', methods=['GET', 'POST'])
def equip_log():
    """Index of equipment log entries or add a new one"""
    if request.method == 'GET':
        logs = EquipmentLog.query.all()
        return jsonify({ 'EquipmentLogs': [equip_log.to_dict() for equip_log in logs] })
    if request.method == 'POST':
        post_data = request.get_json()
        equip_id = post_data.get('equip_id'),
        start_time = datetime.strptime(post_data.get('start_time'), "%d/%m/%Y %H:%M:%S"),
        end_time = datetime.strptime(post_data.get('end_time'), "%d/%m/%Y %H:%M:%S"),
        duration = end_time - start_time

        new_log = EquipmentLog(equipment_id=equip_id, start_time=start_time, end_time=end_time,
          duration=duration)
        try:
            db.session.add(new_log)
            db.session.commit()
            return 'Success'
        except:
            return 'There was an issue adding your the log entry'

@app.route('/equip_chart/<int:enviro_id>', methods=['GET'])
def equip_chart(enviro_id):
    """Index of equipment log entries or add a new one"""
    daily_usage = DailyEquipUsage.query.filter(DailyEquipUsage.date > date.today() - timedelta(days=7)).all()
    equip_list = Equipment.query.all()
    equipment = []
    usage_by_equip = {}
    for equip in equip_list:
        equipment.append(equip.name)
        usage_by_equip[equip.id] = []
        for usage in daily_usage:
            if usage.equipment_id == equip.id:
                usage_by_equip[equip.id].append(usage.runtime)

    return jsonify({ 'equipment': equipment, 'usage': usage_by_equip })

def add_equip_log(equip_log):
    """Handles adding equipment logs whenever a piece of equipment is shutoff,
      automatically calculating the runtime duration in minutes
    """
    equip_id = equip_log['id']
    start_time = datetime.strptime(equip_log['start_time'], "%d/%m/%Y %H:%M:%S")
    end_time = datetime.strptime(equip_log['end_time'], "%d/%m/%Y %H:%M:%S")
    hours = end_time - start_time
    duration = hours.total_seconds()/60

    new_log = EquipmentLog(equipment_id=equip_id, start_time=start_time, end_time=end_time,
        duration=duration)
    try:
        db.session.add(new_log)
        db.session.commit()
        return 'Success'
    except:
        return 'There was an issue adding your the log entry'

def get_day_equip():
    equip_list = []
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    daily_logs = EquipmentLog.query.filter(EquipmentLog.end_time >= yesterday).all()
    equipment = Equipment.query.with_entities(Equipment.id).all()
    for equip in equipment:
        equip_list.append(equip.id)
        
    return daily_logs, equip_list

def upload_daily_equipment(equip_list, equip_usage):
    day = date.today()
    for equip in equip_list:
        runtime = equip_usage[equip]['runtime']
        new_usage = DailyEquipUsage(equipment_id=equip, runtime=runtime, date=day)
        try:
            db.session.add(new_usage)
            db.session.commit()
            return 'Success'
        except:
            return 'There was an issue adding the daily usage'

@app.route('/systems', methods=['GET', 'POST'])
def list_systems():
    """Index of all systems for updating and deleting"""
    if request.method == 'GET':
        systems = System.query.all()
        return jsonify({ 'systems': [system.to_dict() for system in systems] })
    if request.method == 'POST':
        post_data = request.get_json()
        name = post_data.get('name'),
        enviro_id = 1,
        active = post_data.get('active'),
        ideal_ec = post_data.get('ideal_ec'),
        ideal_ph = post_data.get('ideal_ph'),
        ph_variance = post_data.get('ph_variance'),
        ec_variance = post_data.get('ec_variance')

        new_system = System(name=name, enviro_id=enviro_id, active=active, 
          ideal_ec=ideal_ec, ideal_ph=ideal_ph, ec_variance=ec_variance, ph_variance=ph_variance)
        try:
            db.session.add(new_system)
            db.session.commit()
            return 'Success'
        except:
            return 'There was an issue adding your system'

@app.route('/system/<int:id>', methods=['GET', 'DELETE'])
def system_details(id):
    if request.method == 'GET':
        light = {
            'start_time': '00:00',
            'end_time': '00:00'
        }
        ec = []
        ph = []
        water_temp = []
        system = System.query.get(id)
        crops = Crop.query.filter(Crop.system_id == id, Crop.summary == None).all()
        water_logs = Water.query.filter(Water.system_id == id, Water.timestamp > datetime.today() - timedelta(days=30)).all()
        lights = Light.query.filter(Light.system_id == id)
        for light_ in lights:
            light['start_time'] = datetime.strftime(light_.start_time, '%H:%M')
            light['end_time'] = datetime.strftime(light_.end_time, '%H:%M')
        for water in water_logs:
            ec.append(water.ec)
            ph.append(water.ph)
            water_temp.append(water.temp)
        milestones = []
        upcoming_milestones = []
        for crop in crops:
            milestones.append(crop.milestones)
            for milestone in crop.milestones:
                if milestone.actual_date == None:
                    if milestone.projected_date < (date.today() + timedelta(days=10)):
                        upcoming_milestones.append(milestone)
        return jsonify({ 'system': [system.to_dict()],
            'crops': [crop.to_dict() for crop in crops],
            'milestones': [upcoming.to_dict() for upcoming in upcoming_milestones],
            'light': light,
            'ec': ec,
            'ph': ph,
            'water_temp': water_temp,
            'water': [water_log.to_dict() for water_log in water_logs]
        })
    elif request.method == 'DELETE':
        system = System.query.get_or_404(id)
        try:
            db.session.delete(system)
            db.session.commit()
            return 'Success'
        except:
            return 'Failure'

@app.route('/air')
def air_log():
    """Index of all environments for updating and deleting"""
    end = datetime.now()
    start = datetime.now()
    start = timedelta(days=-7)
    inside_temp = []
    inside_humid = []
    outside_temp = []
    timestamps = []

    air_logs = Air.query.order_by(Air.id.desc()).limit(288)

    for air_log in air_logs:
        inside_temp.append(air_log.inside_temp)
        inside_humid.append(air_log.inside_humid)
        outside_temp.append(air_log.outside_temp)
        timestamps.append(air_log.timestamp)

    return jsonify({ 'inside_temps': inside_temp, 'inside_humids': inside_humid, 'outside_temps': outside_temp,
      'timestamps': timestamps
    })

def add_air_log(log):
    time = datetime.now()
    enviro = 1
    i_temp = log['inside_temp']
    o_temp = log['outside_temp']
    i_humid = log['inside_humid']
    o_humid = 0
    
    new_air = Air(timestamp=time, enviro_id=enviro, inside_temp=i_temp, 
      outside_temp=o_temp, outside_humid=o_humid, inside_humid=i_humid)
        
    try:
        db.session.add(new_air)
        db.session.commit()
        return 'Success'
    except:
        return 'There was an issue'

@app.route('/plants', methods=['GET', 'POST'])
def list_plants():
    """Index of all plants for updating and deleting"""
    if request.method == 'GET':
        plants = Plant.query.all()
        plant_names = {}
        categories = PlantCategory.query.all()
        crops = Crop.query.all()
        plant_list = Plant.query.with_entities(Plant.id,Plant.name).all()
        for plant in plant_list:
            plant_names[plant.id] = plant.name

        return jsonify({ 'plants': [plant.to_dict() for plant in plants],
          'categories': [cat.to_dict() for cat in categories],
          'crops': [crop.to_dict() for crop in crops],
          'plant_names': plant_names
          
        })
    elif request.method == 'POST':
        post_data = request.get_json()
        name = post_data.get('name')
        category = post_data.get('category')
        germ_time = post_data.get('germ_time')
        transplant_time = post_data.get('transplant_time')
        flower_time = post_data.get('flower_time')
        harvest_time = post_data.get('harvest_time')
        ideal_ec = post_data.get('ideal_ec')
        ideal_ph = post_data.get('ideal_ph')
        ideal_temp = post_data.get('ideal_temp')
        ideal_humid = post_data.get('ideal_humid')
        ideal_light_hours = post_data.get('ideal_light_hours')    
        ideal_season = post_data.get('ideal_season')
        ideal_medium = post_data.get('ideal_medium')
        ideal_moisture = post_data.get('ideal_moisture')
        support_type = post_data.get('support_type')
        pruning = post_data.get('pruning')
        common_issues = post_data.get('common_issues')

        new_plant = Plant(name=name,category=category,germ_time=germ_time,transplant_time=transplant_time,
          flower_time=flower_time,harvest_time=harvest_time,ideal_ec=ideal_ec,ideal_ph=ideal_ph,
          ideal_temp=ideal_temp,ideal_humid=ideal_humid,ideal_light_hours=ideal_light_hours,
          ideal_season=ideal_season,ideal_medium=ideal_medium,ideal_moisture=ideal_moisture,
          support_type=support_type,pruning=pruning,common_issues=common_issues)
        try:
            db.session.add(new_plant)
            db.session.commit()
            return 'Success'
        except:
            return 'There was an issue adding this plant'

@app.route('/crops', methods=['GET', 'POST'])
def crops():
    """Index of all plants for updating and deleting"""
    if request.method == 'GET':
        plant_names = {}
        crops = Crop.query.all()
        plant_list = Plant.query.with_entities(Plant.id,Plant.name).all()
        for plant in plant_list:
            plant_names[plant.id] = plant.name
        return jsonify({ 'crops': [crop.to_dict() for crop in crops],
          'plant_names': plant_names
        })
    elif request.method == 'POST':
        post_data = request.get_json()
        tag = post_data.get('tag')
        plant_id = post_data.get('plant_id')
        system_id = post_data.get('system_id')
        source = post_data.get('source')
        start_date = post_data.get('start_date')
        
        plant_milestones = Plant.query.get(plant_id)

        new_crop = Crop(tag=tag,plant_id=plant_id,system_id=system_id,source=source,
          start_date=start_date)
        try:
            db.session.add(new_crop)
            db.session.commit()
            msg = add_crop_milestones(plant_milestones)
            return msg
        except:
            msg = add_crop_milestones(plant_milestones)
            return msg

def add_crop_milestones(plant_milestones):
    crop = Crop.query.with_entities(Crop.id, Crop.tag, Crop.start_date, Crop.source).order_by(Crop.id.desc()).first()
    crop_id = crop.id
    germ_time = plant_milestones.germ_time
    transplant_time = plant_milestones.transplant_time
    flower_time = plant_milestones.flower_time
    harvest_time = plant_milestones.harvest_time
    plant = plant_milestones.name
    plant_id = plant_milestones.id
    tag_color = crop.tag
    
    if crop.source == 'Seed':
        projected_germ = crop.start_date + timedelta(days=germ_time)
        germ_milestone = CropMilestone(crop_id=crop_id, plant_name=plant, plant_id=plant_id, tag=tag_color, milestone='Germinate', projected_date=projected_germ)
    if transplant_time != 0:
        projected_transplant = crop.start_date + timedelta(days=transplant_time)
        transplant_milestone = CropMilestone(crop_id=crop_id, plant_name=plant, plant_id=plant_id, tag=tag_color, milestone='Transplant', projected_date=projected_transplant)
    if flower_time != 0:
        projected_flower = crop.start_date + timedelta(days=flower_time)
        flower_milestone = CropMilestone(crop_id=crop_id, plant_name=plant, plant_id=plant_id, tag=tag_color, milestone='Flower', projected_date=projected_flower)
    if harvest_time != 0:
        projected_harvest = crop.start_date + timedelta(days=harvest_time)
        harvest_milestone = CropMilestone(crop_id=crop_id, plant_name=plant, plant_id=plant_id, tag=tag_color, milestone='Harvest', projected_date=projected_harvest)
    
    try:
        if crop.source == 'Seed':
            db.session.add(germ_milestone)
        if transplant_time != 0:
            db.session.add(transplant_milestone)
        if flower_time != 0:
            db.session.add(flower_milestone)
        if harvest_time != 0:
            db.session.add(harvest_milestone)
        db.session.commit()
        return 'Plant Milestones Added'
    except:
        return datetime.strftime(projected_germ)

@app.route('/milestone/<int:id>', methods=['GET', 'POST'])
def updateMilestone(id):
    if request.method == 'POST':
        today = date.today()
        milestone = CropMilestone.query.get(id)
        crop = Crop.query.get(milestone.crop_id)
        if milestone.milestone == 'Germinate':
            crop.germ_date = today
        elif milestone.milestone == 'Transplant':
            crop.transplant_date = today
        elif milestone.milestone == 'Flower':
            crop.flower_date = today
        elif milestone.milestone == 'Harvest':
            crop.harvest_date = today
        milestone.actual_date = today

        try:
            db.session.commit()
            return 'Success'
        except:
            return 'There was an issue'

            
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')