<template>
    <div class="card-2 equip_chart">
      <h2>Equipment Usage</h2>
      <apexchart width="100%" height="250" :options="chartOptions" :series="series">
      </apexchart>
    </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts';

export default {
  name: 'EquipmentChart',
  components: {
    apexchart: VueApexCharts,
  },
  props: ['enviroId'],
  data() {
    return {
      equipment: [],
      usage: [],
      series: [],
      chartOptions: {
        chart: {
          type: 'bar',
          stacked: true,
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom',
            },
          },
        }],
        xaxis: {
          categories: ['Mon', 'Tue'],
        },
        fill: {
          opacity: 1,
        },
        legend: {
          position: 'right',
          offsetX: 0,
          offsetY: 50,
        },
      },
    };
  },
  methods: {
    getDailyEquipUsage() {
      const path = 'http://localhost:5000/equip_chart/1';
      axios.get(path)
        .then((res) => {
          this.equipment = res.data.equipment;
          this.usage = res.data.usage;
          for (let i = 0; i < this.equipment.length; i += 1) {
            this.series.push({
              name: this.equipment[i],
              data: this.usage[i + 1],
            });
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getDailyEquipUsage();
  },
};
</script>
