<template>
  <div>

    <NuxtRouteAnnouncer />
    <NuxtLoadingIndicator :color="'repeating-linear-gradient(to right,#143656 0% ,#0a4c82 100%)'" :height="6" />
    
    <NuxtLayout>
      <NuxtPage class="flex-1" />
    </NuxtLayout>

  </div>
</template>
