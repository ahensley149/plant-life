<template>
    <transition name="fade">
        <vue-flip :active-click="false" width="auto"
          v-model="flip" :class="'sys'+systemOrder+' '+toggle" v-if="toggle == 'show_element'">
          <template v-slot:front>
            <div :class="'card-2 system sys'+systemOrder">
              <h2 class="link" v-on:click="viewSystem()">{{ system[0].name }}</h2>
              <button style="float:right;" v-on:click="flipCard()">Flip</button>
              <div class="notifications_table">
                <span class="table_side_bar">Plnt</span>
                <ul>
                  <li v-for="milestone in milestones" v-bind:key="milestone.id">
                    <div class="tag-color" v-bind:class="milestone.tag"></div>
                    &nbsp;{{ milestone.plant }}&nbsp;
                    {{ milestone.milestone }} by {{ formatDate(milestone.projected_date) }}&nbsp;
                    <button v-on:click="updateMilestone(milestone)">
                      X
                    </button>
                  </li>
                </ul>
              </div>
              <div class="notifications_table">
                <table>
                  <tr>
                    <td>
                      Todos:
                    </td>
                  </tr>
                </table>
              </div>
            </div>
          </template>
          <template v-slot:back>
            <div :class="'card-2 system sys'+systemOrder">
              <h2 class="link" v-on:click="viewSystem()">{{ system[0].name }}</h2>
              <button style="float:right;" v-on:click="flipCard()">Flip</button>
              <div class="crops_table">
                <span class="table_side_bar">Crops</span>
                <ul>
                  <li v-for="crop in crops" v-bind:key="crop.id">
                    <div class="tag-color" v-bind:class="crop.tag"></div>
                    &nbsp;{{ crop.plant[0].name }}&nbsp;
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </vue-flip>
    </transition>
</template>

<script>
import axios from 'axios';
import moment from 'moment';
import VueFlip from 'vue-flip';

export default {
  name: 'Systems',
  props: ['systemId', 'systemOrder', 'toggle'],
  components: {
    'vue-flip': VueFlip,
  },
  data() {
    return {
      system: [],
      milestones: [],
      crops: [],
      flip: false,
    };
  },
  methods: {
    viewSystem() {
      this.$emit('systemIndex', this.systemOrder);
    },
    flipCard() {
      if (this.flip === false) {
        this.flip = true;
      } else {
        this.flip = false;
      }
    },
    formatDate(date) {
      return moment(date).format('MMM Do');
    },
    updateMilestone(milestone) {
      const path = `http://localhost:5000/milestone/${milestone.id}`;
      axios.post(path, milestone.id)
        .then(() => {
          this.getSystem();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    getSystem() {
      const path = `http://localhost:5000/system/${this.systemId}`;
      axios.get(path)
        .then((res) => {
          this.system = res.data.system;
          this.milestones = res.data.milestones;
          this.crops = res.data.crops;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onDelSystem(system) {
      this.delSystem(system[0].id);
    },
  },
  created() {
    this.getSystem();
  },
};
</script>
