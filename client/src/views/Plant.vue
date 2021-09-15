<template>
  <div class="main">
    <div class="dashboard grid-3">
      <button type="button" class="btn btn-success btn-sm" v-b-modal.plant-modal>
        Add plant
      </button>
      <button type="button" class="btn btn-success btn-sm" v-b-modal.crop-modal>
        Add Crop
      </button>
      <Crop :crops="crops" :plantNames="plantNames"></Crop>
      <Plants :plants="plants"></Plants>
    </div>
    <b-modal ref="addPlantModal"
      id="plant-modal"
      title="New Plant"
      hide-footer>
      <form @submit="onSubmit" @reset="onReset" class="w-100">
        <input id="form-title-input"
          type="text"
          v-model="newPlant.name"
          required
          placeholder="Plant Name"/>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.category"
          required>
          <option value=0>
            Type of plant
          </option>
          <option v-for="category in categories"
            v-bind:key="category.id" v-bind:value="category.id">
            {{ category.name }}
          </option>
        </select>
        {{newPlant.category}}
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_ph"
          required
          placeholder="Ideal pH"/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_ec"
          required
          placeholder="Ideal EC"/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_temp"
          required
          placeholder="Ideal Temperature"/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_humid"
          required
          placeholder="Ideal Humidity"/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_light_hours"
          required
          placeholder="Ideal Hours of Light"/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_medium"
          placeholder="Ideal Growing Medium"
          required/>
        <input id="form-title-input"
          type="text"
          v-model="newPlant.ideal_moisture"
          required
          placeholder="Ideal Soil Moisture"/>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.ideal_season"
          required
          placeholder="Ideal Season">
          <option>Spring</option>
          <option>Summer</option>
          <option>Fall</option>
          <option>Winter</option>
        </select>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.germ_time"
          required>
          <option v-for="day in days" v-bind:value="day.value" v-bind:key="day.value">
            {{ day.text }}
          </option>
        </select>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.transplant_time"
          required>
          <option v-for="day in days" v-bind:value="day.value" v-bind:key="day.value">
            {{ day.text }}
          </option>
        </select>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.flower_time"
          required>
          <option v-for="day in days" v-bind:value="day.value" v-bind:key="day.value">
            {{ day.text }}
          </option>
        </select>
        <select id="form-title-input"
          type="text"
          v-model="newPlant.harvest_time"
          required>
          <option v-for="day in days" v-bind:value="day.value" v-bind:key="day.value">
            {{ day.text }}
          </option>
        </select>
        <button type="submit">Submit</button>
      </form>
    </b-modal>
    <b-modal ref="addCropModal"
      id="crop-modal"
      title="New Crop"
      hide-footer>
      <form @submit="submitCrop" @reset="onReset" class="w-100">
        <input id="form-title-input"
          type="text"
          v-model="newCrop.tag"
          required
          placeholder="Tag Color"/>
        <select id="form-title-input"
          type="text"
          v-model="newCrop.plant_id"
          required>
          <option v-for="(plant, index) in plantNames"
            v-bind:key="index" v-bind:value="index">
            {{ plant }}
          </option>
        </select>
        <input id="form-title-input"
          type="text"
          v-model="newCrop.system_id"
          required
          placeholder="System Id"/>
        <input id="form-title-input"
          type="date"
          v-model="newCrop.start_date"
          required/>
        <input id="form-title-input"
          type="text"
          v-model="newCrop.source"
          required
          placeholder="Source"/>
        <button type="submit">Submit</button>
      </form>
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Plants from '@/components/Plants.vue';
import Crop from '@/components/Crop.vue';

export default {
  name: 'Dashboard',
  components: {
    Plants,
    Crop,
  },
  data() {
    return {
      plants: [],
      crops: [],
      categories: [],
      plantNames: [],
      days: [],
      newPlant: {
        name: '',
        category: 0,
        ideal_ec: 2,
        ideal_ph: 6.5,
        ideal_temp: 70,
        ideal_humid: 50,
        ideal_light_hours: 10,
        ideal_medium: '',
        ideal_moisture: '',
        ideal_season: 'Spring',
        germ_time: 6,
        transplant_time: 12,
        flower_time: 50,
        harvest_time: 90,
        pruning: '',
        common_issues: '',
      },
      newCrop: {
        tag: '',
        plant_id: 1,
        system_id: 1,
        source: '',
        start_date: '',
      },
    };
  },
  methods: {
    getPlants() {
      const path = 'http://localhost:5000/plants';
      axios.get(path)
        .then((res) => {
          this.plants = res.data.plants;
          this.categories = res.data.categories;
          this.crops = res.data.crops;
          this.plantNames = res.data.plant_names;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addPlant(payload) {
      // <button type="button" class="btn btn-success btn-sm" v-b-modal.Plant-modal>
      // Add Plant
      // </button>
      const path = 'http://localhost:5000/plants';
      axios.post(path, payload)
        .then(() => {
          this.getPlants();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getPlants();
        });
    },
    addCrop(payload) {
      // <button type="button" class="btn btn-success btn-sm" v-b-modal.Plant-modal>
      // Add Plant
      // </button>
      const path = 'http://localhost:5000/crops';
      axios.post(path, payload)
        .then(() => {
          this.getPlants();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getPlants();
        });
    },
    initForm() {
      this.newPlant.name = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addPlantModal.hide();
      const payload = {
        name: this.newPlant.name,
        category: this.newPlant.category,
        ideal_ec: this.newPlant.ideal_ec,
        ideal_ph: this.newPlant.ideal_ph,
        ideal_temp: this.newPlant.ideal_temp,
        ideal_humid: this.newPlant.ideal_humid,
        ideal_medium: this.newPlant.ideal_medium,
        ideal_moisture: this.newPlant.ideal_moisture,
        ideal_light_hours: this.newPlant.ideal_light_hours,
        ideal_season: this.newPlant.ideal_season,
        germ_time: this.newPlant.germ_time,
        transplant_time: this.newPlant.transplant_time,
        flower_time: this.newPlant.flower_time,
        harvest_time: this.newPlant.harvest_time,
        pruning: this.newPlant.pruning,
        common_issues: this.newPlant.common_issues,
      };
      this.addPlant(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addPlantModal.hide();
      this.initForm();
    },
    submitCrop(evt) {
      evt.preventDefault();
      this.$refs.addCropModal.hide();
      const payloadCrop = {
        tag: this.newCrop.tag,
        plant_id: this.newCrop.plant_id,
        system_id: this.newCrop.system_id,
        source: this.newCrop.source,
        start_date: this.newCrop.start_date,
      };
      this.addCrop(payloadCrop);
    },
    delPlant(plantId) {
      const path = `http://localhost:5000/plant/${plantId}`;
      axios.delete(path)
        .then(() => {
          this.message = 'Plant Deleted';
          this.getPlant(plantId);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getPlants();
    for (let i = 0; i < 100; i += 1) {
      // Runs 5 times, with values of step 0 through 4.
      this.days.push({
        text: `${i} days`,
        value: i,
      });
    }
  },
};
</script>
