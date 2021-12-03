<template>
  <v-app>
    <v-main>
      <Nuxt />
    </v-main>
  </v-app>
</template>

<style lang="scss">
// took from https://www.w3schools.com/howto/howto_css_hide_scrollbars.asp

/* Hide scrollbar for Chrome, Safari and Opera */
body::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
body {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>
