<template>
  <!-- Teleport to App Header -->
  <teleport to="#app-header">
    <div
      class="flex items-center mx-5 md:mr-0 text-p-sm gap-3 text-[14px] mb-[13px]"
    >
      <!-- Source -->
      <div class="flex items-center gap-1">
        <p
          @click="
            copyToClipboard(
              ticket.doc.name,
              `Ticket #${ticket.doc.name} copied to clipboard`
            )
          "
          class="cursor-copy"
        >
          #{{ ticket.doc.name }}
        </p>
        <!-- Via Email -->
        <div
          v-if="!ticket.doc.via_customer_portal"
          class="text-ink-gray-4 flex items-center"
        >
          <span class="text-ink-gray-4 mr-[6px]">via</span>
          <EmailIcon class="size-4 inline-block mr-1" />
          <span class="">Email</span>
        </div>
        <!-- Via Portal -->
        <div v-else class="text-ink-gray-4 flex items-center">
          <span class="text-ink-gray-4 mr-[6px]">via</span>
          <GlobeIcon class="size-4 inline-block mr-1" />
          <span class="font-medium">Portal</span>
        </div>
      </div>
      <!-- divider -->
      <div class="border-l border-outline-gray-2 h-[13px]" />
      <!-- First Response -->
      <div class="flex items-center gap-1">
        <span>{{ __('First Response') }}</span>
        <Badge
          v-if="firstResponse.color"
          :label="firstResponse.label"
          variant="subtle"
          :theme="firstResponse.color"
        />
      </div>
      <!-- divider -->
      <div class="border-l border-outline-gray-2 h-[13px]" />
      <!-- Resolution by -->
      <div class="flex items-center gap-1">
        <span>{{ __('Resolution') }}</span>
        <Badge
          v-if="resolutionBy"
          :label="resolutionBy.label"
          variant="subtle"
          :theme="resolutionBy.color !== 'purple' && resolutionBy.color"
          :class="
            resolutionBy.color === 'purple' && '!text-[#6B46C1] !bg-[#F3E8FF]'
          "
        />
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { __ } from "@/translation";
import { TicketSymbol } from "@/types";
import { copyToClipboard } from "@/utils";
import { dayjs } from "frappe-ui";
import Badge from "frappe-ui/src/components/Badge/Badge.vue";
import { computed, inject } from "vue";

const ticket = inject(TicketSymbol);
const firstResponse = computed<{ label: string; color: "gray" | "blue" | "green" | "orange" | "red" | "" }>(() => {
  if (ticket.value?.get?.loading) return { label: "", color: "" };
  if (
    !ticket.value.doc.first_responded_on &&
    dayjs().isBefore(dayjs(ticket.value.doc.response_by))
  ) {
    let responseBy = formatTimeShort(ticket.value.doc.response_by);
    return {
      label: __('Due in {0}', responseBy),
      color: "orange" as const,
    };
  } else if (
    dayjs(ticket.value.doc.first_responded_on).isBefore(
      dayjs(ticket.value.doc.response_by)
    )
  ) {
    let responseBy = formatTimeShort(
      ticket.value.doc.first_responded_on,
      ticket.value.doc.creation
    );
    return {
      label: __('Fulfilled in {0}', responseBy),
      color: "green" as const,
    };
  } else {
    let responseBy = formatTimeShort(
      String(new Date()),
      ticket.value.doc.response_by
    );
    return {
      label: __('Failed by {0}', responseBy),
      color: "red" as const,
    };
  }
});

const resolutionBy = computed(() => {
  if (ticket.value?.get?.loading) return { label: "", color: "" };

  if (
    ticket.value.doc?.status_category === "Paused" &&
    ticket.value.doc?.on_hold_since &&
    dayjs(ticket.value.doc?.resolution_by).isAfter(
      dayjs(ticket.value.doc?.on_hold_since)
    )
  ) {
    return {
      label: __('On Hold'),
      color: "blue",
    };
  } else if (
    !ticket.value.doc?.resolution_date &&
    dayjs().isBefore(dayjs(ticket.value.doc?.resolution_by))
  ) {
    let resolutionBy = formatTimeShort(ticket.value.doc?.resolution_by);
    return {
      label: __('Due in {0}', resolutionBy),
      color: "purple",
    };
  } else if (
    dayjs(ticket.value.doc?.resolution_date).isBefore(
      dayjs(ticket.value.doc?.resolution_by)
    )
  ) {
    let resolutionBy = formatTimeShort(
      ticket.value.doc?.resolution_date,
      ticket.value.doc?.creation
    );
    return {
      label: __('Fulfilled in {0}', resolutionBy),
      color: "green",
    };
  } else {
    let resolutionBy = formatTimeShort(
      String(new Date()),
      ticket.value.doc?.resolution_by
    );
    return {
      label: __('Failed by {0}', resolutionBy),
      color: "red",
    };
  }
});

function formatTimeShort(date: string, end?: string): string {
  if (!end) {
    end = dayjs().toString();
  }
  let _date = dayjs(date);
  let duration = dayjs.duration(_date.diff(dayjs(end)));

  let days = duration.days();
  let hours = duration.hours();
  let minutes = duration.minutes();

  if (days > 0) {
    return `${days}d ${hours}h`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
}
</script>

<style scoped></style>
