from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/plant_life'
db = SQLAlchemy(app)
db.init_app(app)

# Many to many association table for crops and plants
crop_plants = db.Table('crop_plants',
    db.Column('plant_id', db.Integer, db.ForeignKey('plant.id'), primary_key=True),
    db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'), primary_key=True)
)

class Enviro(db.Model):
    """Enviro is a container for everything in a given grow room or tent or closet. It stores the hygrometer api as well as
      temp and humidity settings and is the direct parent of System(db.Model) for controlling plants on different water tanks.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    hygrometer = db.Column(db.String(255))
    active = db.Column(db.Integer, default=0)
    min_temp = db.Column(db.Integer, default=60)
    max_temp = db.Column(db.Integer, default=80)
    min_humid = db.Column(db.Integer, default=50)
    max_humid = db.Column(db.Integer, default=70)
    systems = db.relationship('System', backref='system')

    def to_dict(self):
        return dict(id=self.id,
          name=self.name,
          hygrometer=self.hygrometer,
          active=self.active,
          min_temp=self.min_temp,
          max_temp=self.max_temp,
          min_humid=self.min_humid,
          max_humid=self.max_humid,
          systems=[system.to_dict() for system in self.systems]
        )

class Air(db.Model):
    """Stores the temperature and Humidity for both inside and outside of the
      grow environment to see if more temp control is needed and track how it affects
      plants.
    """
    id = db.Column(db.Integer, primary_key=True)
    enviro_id = db.Column(db.Integer, db.ForeignKey('enviro.id'))
    timestamp = db.Column(db.DateTime)
    inside_temp = db.Column(db.Integer, default=60)
    inside_humid = db.Column(db.Integer, default=50)
    outside_temp = db.Column(db.Integer, default=80)
    outside_humid = db.Column(db.Integer, default=60)

    def to_dict(self):
        return dict(id=self.id,
          timestamp=self.timestamp,
          inside_temp=self.inside_temp,
          outside_temp=self.outside_temp,
          inside_humid=self.inside_humid,
          outside_humid=self.outside_humid,
          enviro_id=self.enviro_id
        )

class System(db.Model):
    """System groups together plants by their water tanks, allowing for tracking multiple systems in the same grow room,
      for example, if you had a cloner getting new plants ready to drop in your NFT system, they will need different
      nutrient levels from the water.
    """
    id = db.Column(db.Integer, primary_key=True)
    enviro_id = db.Column(db.Integer, db.ForeignKey('enviro.id'))
    name = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Integer, default=0)
    ideal_ph = db.Column(db.Integer, default=6)
    ideal_ec = db.Column(db.Integer, default=2)
    ph_variance = db.Column(db.Float, default=.5)
    ec_variance = db.Column(db.Float, default=.5)

    def to_dict(self):
        return dict(id=self.id,
          name=self.name,
          active=self.active,
          ideal_ph=self.ideal_ph,
          ideal_ec=self.ideal_ec,
          ph_variance=self.ph_variance,
          ec_variance=self.ec_variance,
          enviro_id=self.enviro_id
        )

class WaterTank(db.Model):
    """Stores information on the water reservoir for the system for storing capacity and info on which pumps and valves
      to use in the the testing chamber
    """
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    capacity = db.Column(db.Integer, default=0)
    valve_in = db.Column(db.Integer, default=0)
    valve_out = db.Column(db.Integer, default=0)
    pump = db.Column(db.String(50))
    water_level_sensor = db.Column(db.String(255))

class Schedule(db.Model):
    """Controls the cycle times and durations of watering and other recurring events,
      each water_profile can have multiple cycles for customized schedules or just one
      cycle with recurring times throughout the day
    """
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    start_time = db.Column(db.Time)
    duration = db.Column(db.Integer, default=0)
    recurring = db.Column(db.Integer, nullable=True)

class Equipment(db.Model):
    """Stores information on various equipment used around the room including the api slug to allow control
      of devices through web app.
    """
    id = db.Column(db.Integer, primary_key=True)
    system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=True)
    enviro_id = db.Column(db.Integer, db.ForeignKey('enviro.id'), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    api_slug = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(30))
    status = db.Column(db.Integer, default=0)

class EquipmentLog(db.Model):
    """Stores start, end and duration time for all the equipment in the room to track usage statistics and calculate
      maintenence schedules as well as track their effect on plants.
    """
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

class DailyEquipUsage(db.Model):
    """Stores the daily total run time of each equipment when the backend tallys up all the logs for the day
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    runtime = db.Column(db.Integer, default=0)

    def to_dict(self):
        return dict(id=self.id,
          date=self.date,
          equipment_id=self.equipment_id,
          runtime=self.runtime
        )

class Crop(db.Model):
    """Crop is a link between plants and environments systems to help harvest data on 
      how different plants behave in different environments while still keeping
      both plants and systems reusable and easily updated for future use and
      keeping all the crop data stored for future analysis
    """
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(15))
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'))
    started_as = db.Column(db.String(20), default='Seed')
    plant_date = db.Column(db.Date, nullable=True)
    germ_date = db.Column(db.Date, nullable=True)
    transplant_date = db.Column(db.Date, nullable=True)
    flower_date = db.Column(db.Date, nullable=True)
    harvested_date = db.Column(db.Date, nullable=True)
    harvest_rating = db.Column(db.Integer, default=0)
    harvest_note = db.Column(db.Text)
    logs = db.relationship('Log', backref='log')
    plants = db.relationship('Plant', secondary='crop_plants',
        backref=db.backref('plant', lazy=True))

class Plant(db.Model):
    """Stores Plant profiles containing pertinent plant information to 
      help recommend settings and plant groupings in the future once some 
      data has been harvested
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    germ_time = db.Column(db.Integer)
    transplant_time = db.Column(db.Integer)
    flower_time = db.Column(db.Integer)
    harvest_time = db.Column(db.Integer)
    ideal_ec = db.Column(db.Float, default=2.5)
    ideal_ph = db.Column(db.Float, default=6.5)
    ideal_temp = db.Column(db.Integer, default=65)
    ideal_humid = db.Column(db.Integer, default=60)
    ideal_light_hours = db.Column(db.Integer, default=10)    
    ideal_season = db.Column(db.String(15), nullable=True)
    ideal_medium = db.Column(db.String(50), nullable=True)
    ideal_moisture = db.Column(db.String(50), nullable=True)
    support_type = db.Column(db.String(25))
    pruning = db.Column(db.String(100), nullable=True)
    common_issues = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return dict(id=self.id,
          name=self.name,
          category=self.category
        )

class Photo(db.Model):
    """Stores photo information for crop photos to show progress over time"""
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    file_name = db.Column(db.String(100), nullable=True)
    taken = db.Column(db.DateTime)

class Log(db.Model):
    """Stores different information for crops that doesn't fit in predefined elements
      such as manual tasks performed for outdoor crops not controlled by the automated system
      or just notes that might be useful for future crops
    """
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    body = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(50), default='Note')
    date = db.Column(db.DateTime)
    crops = db.relationship('Crop', backref='log', lazy=True)

class Water(db.Model):
    """Water stores sensor readings either from an automated test systen or manual input for the water tank to
      help track trends in plant growht and nutrient, ph change
    """
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    timestamp = db.Column(db.DateTime)
    ph = db.Column(db.Float, nullable=True)
    ec = db.Column(db.Float, nullable=True)
    temp = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<Water %r>' % self.id

class Light(db.Model):
    """Stores the start and stop time of the lights or if using natural lights, the sunrise and sunset times.
      Also if you have a hygrometer with built in light sensor or standalone can store brightness.
    """
    id = db.Column(db.Integer, primary_key=True)
    enviro_id = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    intensity = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Light %r>' % self.id