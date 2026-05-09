<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";
import { useUserStore } from "./stores/user";

onLaunch(() => {
  const userStore = useUserStore();
  if (userStore.isLoggedIn) {
    userStore.fetchProfile();
  }
});
</script>

<style>
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif;
}
</style>