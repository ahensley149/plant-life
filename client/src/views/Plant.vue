<template>
  <div class="main">
    <div class="dashboard grid-3">
      {{ plants }}
      <Plants></Plants>
    </div>
    <b-modal ref="addPlantModal"
          id="plant-modal"
          title="Add a new plant"
          hide-footer>
          <form @submit="onSubmit" @reset="onReset" class="w-100">
            <input id="form-title-input"
              type="text"
              v-model="newPlant.name"
              required
              placeholder="Enter name"/>
            <input id="form-title-input"
              type="text"
              v-model="newPlant.active"
              required
              placeholder="Active"/>
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
              v-model="newPlant.ph_variance"
              required
              placeholder="pH Variance"/>
            <input id="form-title-input"
              type="text"
              v-model="newPlant.ec_variance"
              required
              placeholder="EC Variance"/>
            <button type="submit">Submit</button>
          </form>
        </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Plants from '@/components/Plants.vue';

export default {
  name: 'Dashboard',
  components: {
    Plants,
  },
  data() {
    return {
      plants: [],
      newPlant: {
        name: '',
        active: 0,
        ideal_ec: 0,
        ideal_ph: 0,
        ph_variance: 0,
        ec_variance: 0,
      },
    };
  },
  methods: {
    getPlants() {
      const path = 'http://localhost:5000/plants';
      axios.get(path)
        .then((res) => {
          this.plants = res.data.plants;
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
    initForm() {
      this.newPlant.name = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addPlantModal.hide();
      const payload = {
        name: this.newPlant.name,
        active: this.newPlant.active,
        ideal_ec: this.newPlant.ideal_ec,
        ideal_ph: this.newPlant.ideal_ph,
        ph_variance: this.newPlant.ph_variance,
        ec_variance: this.newPlant.ec_variance,
      };
      this.addPlant(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addPlantModal.hide();
      this.initForm();
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
  },
};
</script>
