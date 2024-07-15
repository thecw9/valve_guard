<script setup>
import { ref, reactive } from "vue";
import { trainModel, getModelInfoById } from "@/api/model";
import { getHistoryDataByTime, getMeasuresInfoByKey } from "@/api/measures";
import { ElNotification, ElMessage } from "element-plus";
import * as echarts from "echarts";

const emit = defineEmits(["setData"]);
const dialogVisible = ref(false);

const key_store = ref("");

const trainModelForm = reactive({
  key: "",
  name: "",
  trainDataTimeRange: [
    new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
    new Date(),
  ],
});

const modelDetailDrawer = ref(false);
const historyDataDrawer = ref(false);
// last 30 days
const historyDataTimeRange = ref([
  // new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
  new Date(new Date().getTime() - 3600 * 1000 * 24 * 1),
  new Date(),
]);

const shortcuts = [
  {
    text: "今天",
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
    text: "过去一天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24);
      return [start, end];
    },
  },
  {
    text: "过去一周",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "过去一个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  {
    text: "过去三个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
      return [start, end];
    },
  },
];
const historyDataChart = ref();
let historyDataChartInstance = null;
const modelDetailDrawerData = reactive({
  key: "",
  model_name: "",
  time: "",
  current_status: "",
  train_model_file: "",
  train_args: "",
  predict_model_file: "",
  predict_args: "",
  model_train_stdout: "",
  model_train_stderr: "",
});
const historyDataDrawerData = reactive({
  data: [],
});

const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  data: {
    type: Object,
    default: () => [],
  },
});

const tableRowClassName = ({ row, rowIndex }) => {
  if (row.status === "正常") {
    return "success-row";
  } else if (row.status === "报警" || row.status === "异常") {
    return "error-row";
  }
  return "warning-row";
};

const handleOpenTrainModelDialog = async (key) => {
  trainModelForm.key = key;
  trainModelForm.name = "gmm";
  dialogVisible.value = true;
};

const handleTrain = async () => {
  dialogVisible.value = false;
  const res = await trainModel(
    trainModelForm.key,
    trainModelForm.name,
    trainModelForm.trainDataTimeRange[0].toISOString(),
    trainModelForm.trainDataTimeRange[1].toISOString(),
  );
  if (res.code === 200) {
    ElNotification({
      title: "成功",
      message: "训练成功",
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
};

const handleOpenModelDetailDrawer = () => {};

const handleOpenHistoryDataDrawer = () => {
  historyDataChartInstance = echarts.init(historyDataChart.value);
  window.addEventListener("resize", () => {
    historyDataChartInstance.resize();
  });
};

const handleCloseModelDetailDrawer = () => {};

const handleCloseHistoryDataDrawer = () => {
  historyDataChartInstance.dispose();
};

const handleViewModelDetailDrawer = async (key) => {
  modelDetailDrawer.value = true;
  const res = await getModelInfoById(key);
  if (res.code === 200) {
    modelDetailDrawerData.key = res.data.key;
    modelDetailDrawerData.model_name = res.data.name;
    modelDetailDrawerData.time = res.data.time;
    modelDetailDrawerData.current_status = res.data.current_status;
    modelDetailDrawerData.train_model_file = res.data.train_model_file;
    modelDetailDrawerData.train_args = res.data.train_args;
    modelDetailDrawerData.predict_model_file = res.data.predict_model_file;
    modelDetailDrawerData.predict_args = res.data.predict_args;
    modelDetailDrawerData.model_train_stdout = res.data.model_train_stdout;
    modelDetailDrawerData.model_train_stderr = res.data.model_train_stderr;
  }
};

const handleViewHistoryDataDrawer = async (key) => {
  historyDataDrawer.value = true;
  key_store.value = key;
  setHistoryData();
};

const setHistoryData = async () => {
  const res = await getHistoryDataByTime(
    key_store.value,
    historyDataTimeRange.value[0],
    historyDataTimeRange.value[1],
  );
  if (res.code === 200) {
    const historyData = res.data
      .map((item) => {
        return {
          time: item.timestamp?.replace("T", " ").split(".")[0],
          value: item.value,
        };
      })
      .sort((a, b) => {
        return new Date(a.service_time) - new Date(b.service_time);
      });
    historyDataDrawerData.data = historyData;
    historyDataChartInstance.setOption({
      title: {
        text: "历史数据",
        left: "center",
        textStyle: {
          color: "#ccc",
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross",
        },
      },
      xAxis: {
        type: "category",
        data: historyData.map((item) => item.time),
      },
      yAxis: {
        type: "value",
        min:
          Math.min(...historyData.map((item) => item.value)) -
          (Math.max(...historyData.map((item) => item.value)) -
            Math.min(...historyData.map((item) => item.value))) *
            0.2,
        max:
          Math.max(...historyData.map((item) => item.value)) +
          (Math.max(...historyData.map((item) => item.value)) -
            Math.min(...historyData.map((item) => item.value))) *
            0.2,
        splitLine: {
          show: false,
        },
      },
      series: [
        {
          data: historyData.map((item) => item.value),
          type: "line",
          smooth: true,
        },
      ],
    });
  }
};
</script>

<template>
  <!-- 训练弹窗 -->
  <el-dialog v-model="dialogVisible" title="训练模型" width="50%">
    <el-form-item label="测点编号">
      <el-input v-model="trainModelForm.key" disabled />
    </el-form-item>
    <el-form label-width="80px">
      <el-form-item label="模型名称">
        <el-select v-model="trainModelForm.name" placeholder="please select">
          <el-option label="gmm" value="gmm" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间范围">
        <el-date-picker
          v-model="trainModelForm.trainDataTimeRange"
          type="datetimerange"
          :shortcuts="shortcuts"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button class="cancel-btn" @click="dialogVisible = false"
          >取消</el-button
        >
        <el-button type="primary" @click="handleTrain">确认训练</el-button>
      </span>
    </template>
  </el-dialog>

  <div>
    <h1>{{ props.title }}</h1>
    <div class="table-box">
      <el-table :data="props.data" border style="width: 100%">
        <el-table-column prop="key" label="测点编号" align="center" />
        <el-table-column prop="path" label="测点" align="center" />
        <el-table-column prop="time" label="时间" align="center" />
        <el-table-column prop="value" label="值" align="center" width="140" />
        <el-table-column prop="unit" label="单位" align="center" width="100" />
        <el-table-column label="操作" align="center" fixed="right" width="320">
          <template #default="scope">
            <el-button
              type="danger"
              @click="handleOpenTrainModelDialog(scope.row.key)"
              >训练模型</el-button
            >
            <el-button @click="handleViewModelDetailDrawer(scope.row.key)"
              >模型详情</el-button
            >
            <el-button @click="handleViewHistoryDataDrawer(scope.row.key)"
              >历史数据</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 模型详情抽屉 -->
    <el-drawer
      v-model="modelDetailDrawer"
      title="模型详情"
      size="90%"
      @open="handleOpenModelDetailDrawer"
      @closed="handleCloseModelDetailDrawer"
    >
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
      <el-button @click="handleTrain(modelDetailDrawerData.key)"
        >训练模型</el-button
      >
      <el-divider></el-divider>
      <span>测点编号：{{ modelDetailDrawerData.key }}</span>
      <span>模型名称：{{ modelDetailDrawerData.model_name }}</span>
      <span>时间：{{ modelDetailDrawerData.time }}</span>
      <span>当前状态：{{ modelDetailDrawerData.current_status }}</span>
      <span>训练模型文件：{{ modelDetailDrawerData.train_model_file }}</span>
      <span>训练参数：{{ modelDetailDrawerData.train_args }}</span>
      <span>预测模型文件：{{ modelDetailDrawerData.predict_model_file }}</span>
      <span>预测参数：{{ modelDetailDrawerData.predict_args }}</span>
      <span>训练输出：{{ modelDetailDrawerData.model_train_stdout }}</span>
      <span>训练错误：{{ modelDetailDrawerData.model_train_stderr }}</span>
    </el-drawer>

    <!-- 历史数据抽屉 -->
    <el-drawer
      v-model="historyDataDrawer"
      title="历史数据"
      size="90%"
      @open="handleOpenHistoryDataDrawer"
      @closed="handleCloseHistoryDataDrawer"
    >
      <el-date-picker
        v-model="historyDataTimeRange"
        type="datetimerange"
        :shortcuts="shortcuts"
        range-separator="To"
        start-placeholder="Start date"
        end-placeholder="End date"
      />
      <el-button @click="setHistoryData">查询</el-button>
      <el-divider></el-divider>
      <div ref="historyDataChart" style="width: 100%; height: 300px"></div>
      <el-table
        :data="historyDataDrawerData.data"
        border
        style="width: 100%"
        height="650"
      >
        <el-table-column prop="time" label="时间" align="center" />
        <el-table-column prop="value" label="值" align="center" />
      </el-table>
    </el-drawer>
  </div>
</template>

<style scoped>
span {
  display: flex;
  font-size: 16px;
}
</style>
