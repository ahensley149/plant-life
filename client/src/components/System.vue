<template>
    <transition name="slide">
      <div class="card-2 card-large system sys" v-if="toggle === 'show_element'">
        <h2>{{ getLightStatus() }}{{ value.name }}
          <button v-on:click="closeSystemView">X</button>
        </h2>
        <div class="flex_row">
          <apexchart width="100%" height="300" type="line" :options="options" :series="series">
          </apexchart>
          <div class="crops_list">
            <h3>Current Crops
              <button type="button" class="btn btn-success btn-sm" v-b-modal.crop-modal>
                +
              </button>
            </h3>
            <select v-model="selectedCrops" multiple class="crop_select">
              <option v-for="crop in crops"
                v-bind:key="crop.id"
                v-bind:value="crop.id">
                <div class="tag-color" v-bind:class="crop.tag"></div>
                &nbsp;{{ crop.plant[0].name }}&nbsp;
              </option>
            </select>
            <li>
              <select v-model="log">
                <option value="Details">
                  Detail View
                </option>
                <option value="Log">
                  New Log
                </option>
                <option value="Disease">
                  Disease
                </option>
                <option value="Task">
                  Manual Task
                </option>
              </select>
              <b-button>Go</b-button>
            </li>
          </div>
        </div>
        <b-modal ref="addCropModal"
          id="crop-modal"
          title="New Crop"
          hide-footer>
          <form @submit="submitCrop" class="w-100">
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
    </transition>
</template>

<script>
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts';

export default {
  name: 'System',
  props: ['value', 'toggle'],
  components: {
    apexchart: VueApexCharts,
  },
  data() {
    return {
      systemId: this.value.id,
      log: 'Details',
      light: {},
      allCrops: true,
      selectedCrops: [],
      lightStatus: false,
      system: [],
      crops: [],
      plantNames: [],
      newCrop: {
        tag: '',
        plant_id: 1,
        system_id: this.value.id,
        source: '',
        start_date: '',
      },
      options: {
        chart: {
          id: 'vuechart-example',
        },
        xaxis: {
          type: 'category',
          categories: [],
          tickPlacement: 'between',
        },
        yaxis: [
          {
            title: {
              text: 'EC',
            },
          },
          {
            title: {
              text: 'PH',
            },
          },
          {
            title: {
              text: 'Temp',
            },
            seriesName: 'Water Temp',
            opposite: true,
          },
        ],
      },
      series: [],
    };
  },
  watch: {
    value() {
      this.getSystem();
    },
  },
  methods: {
    addCrop(payload) {
      const path = 'http://localhost:5000/crops';
      axios.post(path, payload)
        .then(() => {
          this.getSystem();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getSystem();
        });
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
    closeSystemView() {
      this.$emit('close-sys-view', true);
    },
    getSystem() {
      const path = `http://localhost:5000/system/${this.value.id}`;
      axios.get(path)
        .then((res) => {
          this.system = res.data.system;
          this.crops = res.data.crops;
          this.light = res.data.light;
          this.series = [
            {
              name: 'EC',
              data: res.data.ec,
            },
            {
              name: 'pH',
              data: res.data.ph,
            },
            {
              name: 'Water Temp',
              data: res.data.water_temp,
            },
          ];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getLightStatus() {
      const today = new Date();
      const time = today.getHours();
      const startTime = parseInt(this.light.start_time.substring(0, 2), 10);
      const endTime = parseInt(this.light.end_time.substring(0, 2), 10);
      if (startTime > endTime) {
        if (time > startTime || time < endTime) {
          this.lightStatus = true;
        }
      } else {
        this.lightStatus = false;
        if (time > startTime && time < endTime) {
          this.lightStatus = true;
        }
      }
    },
    getPlantNames() {
      const path = 'http://localhost:5000/plants';
      axios.get(path)
        .then((res) => {
          this.plantNames = res.data.plant_names;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onDelSystem(system) {
      this.delSystem(system.id);
    },
  },
  created() {
    this.getSystem();
    this.getPlantNames();
  },
};
</script>
