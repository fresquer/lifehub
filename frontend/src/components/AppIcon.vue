<template>
  <component
    :is="iconComponent"
    :size="size"
    :stroke-width="strokeWidth"
    aria-hidden="true"
  />
</template>

<script setup>
import { computed } from "vue";
import {
  PROJECT_ICON_MAP,
  DEFAULT_PROJECT_ICON,
} from "./projectIcons.js";

const props = defineProps({
  /** Lucide icon name (e.g. 'FileText'). Unknown or legacy emoji fallback to FileText. */
  name: { type: String, default: DEFAULT_PROJECT_ICON },
  size: { type: Number, default: 24 },
  strokeWidth: { type: Number, default: 2 },
});

const iconComponent = computed(() => {
  const name = props.name && PROJECT_ICON_MAP[props.name] ? props.name : DEFAULT_PROJECT_ICON;
  return PROJECT_ICON_MAP[name];
});
</script>
