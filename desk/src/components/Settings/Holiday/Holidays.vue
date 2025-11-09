<template>
  <div class="px-10 py-8">
    <SettingsLayoutHeader
      :title="__('Business Holidays')"
      description="Set your team’s working days, hours, and holidays using a template or custom schedule."
    >
      <template #actions>
        <Button
          :label="__('New')"
          theme="gray"
          variant="solid"
          @click="goToNew()"
          icon-left="plus"
        />
      </template>
    </SettingsLayoutHeader>
  </div>
  <div class="overflow-y-auto pb-8 px-10">
    <HolidayList />
  </div>
</template>

<script setup lang="ts">
import {
  holidayListActiveScreen,
  resetHolidayData,
} from "@/stores/holidayList";
import HolidayList from "./HolidayList.vue";
import SettingsLayoutHeader from "../SettingsLayoutHeader.vue";
import { __ } from "@/translation";
const goToNew = () => {
  resetHolidayData();
  holidayListActiveScreen.value = {
    screen: "view",
    data: null,
  };
};
</script>
