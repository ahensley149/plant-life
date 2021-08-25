from flask import jsonify, request
from flask_cors import CORS
from models import *
from datetime import datetime, date, timedelta

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/enviros')
def list_environments():
    """Index of all environments for updating and deleting"""
    enviros = Enviro.query.all()
    enviro = Enviro.query.get_or_404(1)
    return jsonify({ 'enviros': [env.to_dict() for env in enviros],
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
        system = System.query.get(id)
        return jsonify({ 'system': [system.to_dict()] })
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

@app.route('/plants')
def list_plants():
    """Index of all plants for updating and deleting"""
    plants = Plant.query.all()
    return jsonify({ 'plants': [plant.to_dict() for plant in plants]})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')