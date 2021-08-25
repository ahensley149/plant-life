<template>
  <div class="nav">
    <router-link to="/">
      <img width="60px" src="../assets/nav/hf-icon.png">
    </router-link>
    <br /><br />
    <router-link class="nav_link" to="/">
      <img class="nav_img" src="../assets/nav/environment1.png">
    </router-link>
    <br /><br />
    <router-link class = "nav_link" to="/plants">
      <img class="nav_img"  src="../assets/nav/plant1.png">
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Nav',
  props: {
    msg: String,
  },
};
</script>
