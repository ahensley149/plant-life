<template>
    <div class="card-2 air_chart">
      <h2>
        Climate Control
        <button v-on:click="submitUpdate(tempRange[0],
          tempRange[1], humidRange[0], humidRange[1])">
          +
        </button>
      </h2>
      <VueSimpleRangeSlider
        style="width: 100%"
        :min="0"
        :max="100"
        v-model="tempRange"
      />
      Current Temp: {{ insideTemps[0] }}*
      <VueSimpleRangeSlider
        style="width: 100%"
        :min="0"
        :max="100"
        v-model="humidRange"
      />
      Current Humidity: {{ insideHumids[0] }}%
      <br />
      <apexchart width="100%" height="200" type="line" :options="options" :series="series">
      </apexchart>
    </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts';
import VueSimpleRangeSlider from 'vue-simple-range-slider';
import 'vue-simple-range-slider/dist/vueSimpleRangeSlider.css';

export default {
  name: 'AirChart',
  components: {
    apexchart: VueApexCharts,
    VueSimpleRangeSlider,
  },
  props: ['enviro'],
  data() {
    return {
      tempRange: [],
      humidRange: [],
      min_temp: [],
      insideTemps: [],
      outsideTemps: [],
      insideHumids: [],
      options: {
        chart: {
          id: 'vuechart-example',
        },
        xaxis: {
          categories: [1],
        },
      },
      series: [],
    };
  },
  methods: {
    getAir() {
      const path = 'http://localhost:5000/air';
      axios.get(path)
        .then((res) => {
          this.insideTemps = res.data.inside_temps;
          this.outsideTemps = res.data.outside_temps;
          this.insideHumids = res.data.inside_humids;
          this.series = [
            {
              name: 'Inside Temp',
              data: this.insideTemps,
            },
            {
              name: 'Inside Humidity',
              data: this.insideHumids,
            },
            {
              name: 'Outside Temp',
              data: this.outsideTemps,
            },
            this.tempRange = [this.enviro.min_temp, this.enviro.max_temp],
            this.humidRange = [this.enviro.min_humid, this.enviro.max_humid],
          ];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    submitUpdate(minTemp, maxTemp, minHumid, maxHumid) {
      const payload = {
        min_temp: minTemp,
        max_temp: maxTemp,
        min_humid: minHumid,
        max_humid: maxHumid,
      };
      this.updateClimate(payload, this.enviro.id);
    },
    updateClimate(payload, enviroId) {
      const path = `http://localhost:5000/update_climate/${enviroId}`;
      axios.post(path, payload)
        .then(() => {
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getAir();
  },
};
</script>
