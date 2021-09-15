<template>
  <div class="card-2 crops">
    <div class="crops">
      <ul>
        <li v-for="crop in crops" v-bind:key="crop.id">
          {{ crop.tag }} - {{ plantNames[crop.plant_id] }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Crop',
  props: ['crops', 'plantNames'],
};
</script>
