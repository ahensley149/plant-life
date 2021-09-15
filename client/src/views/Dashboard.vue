<template>
  <div class="main">
    <div class="dashboard grid-3">
      <AirChart :enviro="enviro[0]"></AirChart>
      <Systems v-for="(system, index) in enviro[0].systems" :key="index"
        :systemId="system.id"
        :systemOrder="index"
        @systemIndex="onClickSystem"
        :toggle="indexSystems">
      </Systems>
      <EquipmentChart :enviroId="enviro[0].id"></EquipmentChart>
        <System v-model="enviro[0].systems[system]"
          :toggle="viewSystem"
          @close-sys-view="closeSystem">
        </System>
    </div>
    <b-modal ref="addSystemModal"
          id="system-modal"
          title="Add a new system"
          hide-footer>
          <form @submit="onSubmit" @reset="onReset" class="w-100">
            <input id="form-title-input"
              type="text"
              v-model="newSystem.name"
              required
              placeholder="Enter name"/>
            <input id="form-title-input"
              type="text"
              v-model="newSystem.active"
              required
              placeholder="Active"/>
            <input id="form-title-input"
              type="text"
              v-model="newSystem.ideal_ph"
              required
              placeholder="Ideal pH"/>
            <input id="form-title-input"
              type="text"
              v-model="newSystem.ideal_ec"
              required
              placeholder="Ideal EC"/>
            <input id="form-title-input"
              type="text"
              v-model="newSystem.ph_variance"
              required
              placeholder="pH Variance"/>
            <input id="form-title-input"
              type="text"
              v-model="newSystem.ec_variance"
              required
              placeholder="EC Variance"/>
            <button type="submit">Submit</button>
          </form>
        </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Systems from '@/components/Systems.vue';
import System from '@/components/System.vue';
import AirChart from '@/components/Air.vue';
import EquipmentChart from '@/components/Equipment.vue';

export default {
  name: 'Dashboard',
  components: {
    Systems,
    System,
    AirChart,
    EquipmentChart,
  },
  data() {
    return {
      enviros: [],
      enviro: [],
      viewSystem: 'hide_element',
      indexSystems: 'show_element',
      system: 0,
      newSystem: {
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
    onClickSystem(value) {
      this.system = value;
      this.indexSystems = 'hide_element';
      setTimeout(() => { this.viewSystem = 'show_element'; }, 500);
    },
    closeSystem() {
      this.viewSystem = 'hide_element';
      setTimeout(() => { this.indexSystems = 'show_element'; }, 1000);
    },
    getEnviros() {
      const path = 'http://localhost:5000/enviros';
      axios.get(path)
        .then((res) => {
          this.enviros = res.data.enviros;
          this.enviro = res.data.enviro;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addSystem(payload) {
      // <button type="button" class="btn btn-success btn-sm" v-b-modal.system-modal>
      // Add System
      // </button>
      const path = 'http://localhost:5000/systems';
      axios.post(path, payload)
        .then(() => {
          this.getEnviros();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getSystem();
        });
    },
    initForm() {
      this.newSystem.name = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addSystemModal.hide();
      const payload = {
        name: this.newSystem.name,
        active: this.newSystem.active,
        ideal_ec: this.newSystem.ideal_ec,
        ideal_ph: this.newSystem.ideal_ph,
        ph_variance: this.newSystem.ph_variance,
        ec_variance: this.newSystem.ec_variance,
      };
      this.addSystem(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addSystemModal.hide();
      this.initForm();
    },
    delSystem(sysId) {
      const path = `http://localhost:5000/system/${sysId}`;
      axios.delete(path)
        .then(() => {
          this.message = 'System Deleted';
          this.getSystem(sysId);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getEnviros();
  },
};
</script>
