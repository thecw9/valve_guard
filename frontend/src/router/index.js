import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/LoginView.vue"),
  },
  {
    path: "/index",
    name: "index",
    redirect: "/monitor/sound",
    component: () => import("@/views/IndexView.vue"),
    children: [
      // {
      //   path: "/home",
      //   name: "home",
      //   meta: { title: "首页", icon: "menu" },
      //   component: () => import("@/views/home/index.vue"),
      // },
      {
        path: "/monitor/sound",
        name: "sound",
        meta: { title: "声纹监测", icon: "menu" },
        component: () => import("@/views/sound/index.vue"),
      },
      {
        path: "/monitor/waveform",
        name: "waveform",
        meta: { title: "波形监测", icon: "menu" },
        component: () => import("@/views/waveform/index.vue"),
      },
      {
        path: "/monitor/fft",
        name: "fft",
        meta: { title: "FFT监测", icon: "menu" },
        component: () => import("@/views/fft/index.vue"),
      },
      {
        path: "/monitor/spectrogram",
        name: "spectrogram",
        meta: { title: "频谱监测", icon: "menu" },
        component: () => import("@/views/spectrogram/index.vue"),
      },
      // {
      //   path: "/monitor/part-discharge",
      //   name: "part-discharge",
      //   meta: { title: "局放监测", icon: "menu" },
      //   component: () => import("@/views/part-discharge/index.vue"),
      // },
      // {
      //   path: "/monitor/iron-core",
      //   name: "iron-core",
      //   meta: { title: "铁芯夹件监测", icon: "menu" },
      //   component: () => import("@/views/iron-core/index.vue"),
      // },
      // {
      //   path: "/monitor/sf6",
      //   name: "sf6",
      //   meta: { title: "SF6气体监测", icon: "menu" },
      //   component: () => import("@/views/sf6/index.vue"),
      // },
      // {
      //   path: "/monitor/sound",
      //   name: "sound",
      //   meta: { title: "声音监测", icon: "menu" },
      //   component: () => import("@/views/sound/index.vue"),
      // },
      // {
      //   path: "/monitor/overall",
      //   name: "overall",
      //   meta: { title: "综合监测", icon: "menu" },
      //   component: () => import("@/views/overall/index.vue"),
      // },
      // {
      //   path: "/alarm",
      //   name: "alarm",
      //   meta: { title: "告警管理", icon: "menu" },
      //   component: () => import("@/views/alarm/index.vue"),
      // },
      // {
      //   path: "/train_logs",
      //   name: "train_logs",
      //   meta: { title: "训练日志", icon: "menu" },
      //   component: () => import("@/views/train_logs/index.vue"),
      // },
      {
        path: "/model-management",
        name: "model-management",
        meta: { title: "模型管理", icon: "menu" },
        component: () => import("@/views/model-management/index.vue"),
      },
      // {
      //   path: "/monitor/video",
      //   name: "video",
      //   meta: { title: "视频监测", icon: "menu" },
      //   component: () => import("@/views/video/index.vue"),
      // },
      // {
      //   path: "/report",
      //   name: "report",
      //   meta: { title: "预警报告", icon: "menu" },
      //   component: () => import("@/views/report/index.vue"),
      // },
      {
        path: "/user",
        name: "user",
        meta: { title: "用户管理", icon: "menu" },
        component: () => import("@/views/user/index.vue"),
      },
      {
        path: "/about",
        name: "about",
        meta: { title: "关于", icon: "menu" },
        component: () => import("@/views/about/index.vue"),
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*", // 404
    name: "NotFound",
    component: () => import("@/views/NotFoundView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
