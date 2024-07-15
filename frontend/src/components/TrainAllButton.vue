<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { trainModel } from "@/api/model";
import { trainFusionModel } from "@/api/fusion_model";
import { ElNotification, ElMessage } from "element-plus";
import { deleteAllTrainLogs } from "@/api/trainlogs";

const emit = defineEmits(["setData"]);

const router = useRouter();

const dialogVisible = ref(false);
const trainDataTimeRange = ref([
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(),
]);

const shortcuts = [
  {
    text: "Today",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setHours(0);
      start.setMinutes(0);
      start.setSeconds(0);
      return [start, end];
    },
  },
  {
    text: "Last 1 day",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24);
      return [start, end];
    },
  },
  {
    text: "Last week",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "Last month",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  {
    text: "Last 3 months",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
      return [start, end];
    },
  },
];

const props = defineProps({
  fusion: {
    type: Boolean,
    default: false,
  },
  data: {
    type: Object,
    default: () => [],
  },
});

const handleViewTrainLogs = () => {
  // 跳转到/train-logs
  router.push("/train_logs");
};

const handleTrainAll = async () => {
  let res = null;
  if (props.fusion) {
    res = await trainFusionModel(
      props.data.map((item) => item.key),
      trainDataTimeRange.value[0],
      trainDataTimeRange.value[1],
    );
  } else {
    res = await trainModel(
      props.data.map((item) => item.key),
      trainDataTimeRange.value[0],
      trainDataTimeRange.value[1],
    );
  }
  if (res.code === 200) {
    ElNotification({
      title: "模型训练",
      message: "模型训练任务加入后台任务队列",
      type: "success",
    });
    // sleep 1s
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 500);
    });
    emit("setData");
  } else {
    ElMessage.error("失败");
  }
  dialogVisible.value = false;
};

const handleDeleteAllTrainLogs = async () => {
  ElMessageBox.confirm("确认清空训练日志？")
    .then(async () => {
      const res = await deleteAllTrainLogs();
      if (res.code === 200) {
        ElNotification({
          title: "清空训练日志",
          message: "清空训练日志成功",
          type: "success",
        });
      } else {
        ElMessage.error("清空训练日志失败");
      }
    })
    .catch(() => {});
};
</script>

<template>
  <el-button type="primary" @click="dialogVisible = true">全部训练</el-button>
  <el-button type="primary" @click="handleViewTrainLogs"
    >查看训练日志</el-button
  >
  <el-button type="primary" @click="handleDeleteAllTrainLogs"
    >清空训练日志</el-button
  >

  <!-- 全部训练弹窗 -->
  <el-dialog v-model="dialogVisible" title="训练模型" width="50%">
    <span style="margin-bottom: 10px; font-size: 18px"
      >选择训练数据时间范围：</span
    >
    <el-date-picker
      v-model="trainDataTimeRange"
      type="datetimerange"
      :shortcuts="shortcuts"
      range-separator="To"
      start-placeholder="Start date"
      end-placeholder="End date"
    />
    <template #footer>
      <span class="dialog-footer">
        <el-button class="cancel-btn" @click="dialogVisible = false"
          >取消</el-button
        >
        <el-button type="primary" @click="handleTrainAll">确认训练</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>
.header {
  width: 100%;
  height: 60px;
  background-color: #545c6410;
  @apply flex items-center;
}

.breadcrumb_text {
  color: #fff;

  &:hover {
    color: #409eff;
  }
}

.exit-btn {
  position: absolute;
  right: 20px;
}
</style>
