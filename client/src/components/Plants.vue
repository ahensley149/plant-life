<template>
  <div class="card-2 plants">
    <div class="plants">
      <ul>
        <li v-for="plant in plants" v-bind:key="plant.id">
          {{ plant.name }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Plants',
  props: ['plants'],
};
</script>
