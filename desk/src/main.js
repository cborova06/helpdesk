import { createApp, h } from "vue";
import {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  frappeRequest,
  FrappeUI,
  Input,
  setConfig,
  TextInput,
  toast,
  Tooltip,
} from "frappe-ui";
import { createPinia } from "pinia";
import App from "./App.vue";
import { createDialog } from "./components/dialogs";
import "./index.css";
import { router } from "./router";
import { posthogPlugin } from "./telemetry";
import { isCustomerPortal } from "@/utils";
import { translationPlugin } from "./translation";
import CircleAlert from "~icons/lucide/circle-alert";
import { initSocket } from "./socket";

// Safety shim: prevent ResizeObserver.observe from throwing when a Vue component
// instance (with $el) or a falsy/invalid target is passed by third-party components.
if (typeof window !== "undefined" && typeof window.ResizeObserver !== "undefined") {
  const NativeResizeObserver = window.ResizeObserver;
  // Avoid double-patching
  if (NativeResizeObserver && NativeResizeObserver.name !== "SafeResizeObserver") {
    class SafeResizeObserver extends NativeResizeObserver {
      observe(target, options) {
        // Prefer the raw Element if available
        const el = target?.nodeType === 1 ? target : target?.$el?.nodeType === 1 ? target.$el : null;
        if (el) {
          return super.observe(el, options);
        }
        // If the element isn't ready yet (e.g., called before mount), try once on next frame
        // instead of throwing, so libraries relying on RO don't break initialization.
        if (target && target.$el === undefined) {
          // Non-element, non-Vue object: skip silently
          return;
        }
        requestAnimationFrame(() => {
          const nextEl = target?.$el?.nodeType === 1 ? target.$el : null;
          if (nextEl) {
            try {
              super.observe(nextEl, options);
            } catch (_) {
              // no-op: best-effort fallback
            }
          }
        });
        // Spec returns void
      }
    }
    window.ResizeObserver = SafeResizeObserver;
  }
}

const globalComponents = {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  Input,
  Tooltip,
  TextInput,
};

setConfig("resourceFetcher", frappeRequest);
setConfig("serverMessagesHandler", (msgs) => {
  if (isCustomerPortal.value) {
    return;
  }
  msgs.forEach((msg) => {
    msg = JSON.parse(msg);
    if (msg && msg.message == "Feedback email has been sent to the customer") {
      toast.success(msg.message);
      return;
    }
    toast.create({
      message: msg.message,
      icon: h(CircleAlert, { class: "text-blue-500" }),
    });
  });
});
setConfig("fallbackErrorHandler", (error) => {
  const msg = error.exc_type
    ? (error.messages || error.message || []).join(", ")
    : error.message;
  toast.error(msg);
});

const pinia = createPinia();
const app = createApp(App);

app.use(FrappeUI);
app.use(pinia);
app.use(router);
app.use(posthogPlugin);
app.use(translationPlugin);

for (const c in globalComponents) {
  app.component(c, globalComponents[c]);
}

app.config.globalProperties.$dialog = createDialog;

let socket;
if (import.meta.env.DEV) {
  frappeRequest({
    url: "/api/method/helpdesk.www.helpdesk.index.get_context_for_dev",
  }).then((values) => {
    for (let key in values) {
      window[key] = values[key];
    }
    socket = initSocket();
    app.config.globalProperties.$socket = socket;
    app.mount("#app");
  });
} else {
  socket = initSocket();
  app.config.globalProperties.$socket = socket;
  app.mount("#app");
}
