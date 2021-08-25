<template>
    <div :class="'card-2 system sys'+systemOrder">
      <h2>{{ system[0].name }}</h2>
    </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Systems',
  props: ['systemId', 'systemOrder'],
  data() {
    return {
      system: [],
    };
  },
  methods: {
    getSystem() {
      const path = `http://localhost:5000/system/${this.systemId}`;
      axios.get(path)
        .then((res) => {
          this.system = res.data.system;
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
