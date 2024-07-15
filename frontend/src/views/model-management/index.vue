<script setup>
import { ref, reactive, watch, onMounted } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import { trainModel, getModelInfo, getModelInfoById } from "@/api/model";
import { ElNotification, ElMessage } from "element-plus";
import { formatNumber } from "@/utils/index";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const modelDetailDrawer = ref(false);
const dialogVisible = ref(false);
const form = reactive({
  include: "韶山站 声音",
  exclude: "",
});
const modelDetailDrawerData = ref({});

const trainModelForm = reactive({
  key: "",
  name: "",
  trainDataTimeRange: [
    new Date(new Date().getTime() - 3600 * 1000 * 24 * 30),
    new Date(),
  ],
});

const trainModelDialogVisible = ref(false);

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

const handleOpenTrainModelDialog = async (key) => {
  trainModelForm.key = key;
  trainModelForm.name = "gmm";
  dialogVisible.value = true;
};

const setData = async () => {
  await getModelInfo(
    form.include.replace(/ /g, "&"),
    form.exclude.replace(/ /g, "&"),
  ).then((res) => {
    if (res.code === 200) {
      data.value = res.data.map((item) => {
        return {
          _id: item._id,
          key: item.key,
          path: item.path,
          model_name: item.name,
          time: item.time,
          current_status: item.current_status,
          train_model_file: item.train_model_file,
          train_args: item.train_args,
          predict_model_file: item.predict_model_file,
          predict_args: item.predict_args,
          model_train_stdout: item.model_train_stdout,
          model_train_stderr: item.model_train_stderr,
        };
      });
      ElNotification({
        title: "查询成功",
        message: "数据查询成功",
        type: "success",
      });
    }
  });
};

const tableRowClassName = ({ row, rowIndex }) => {
  if (row.train_model_file === "正常") {
    return "success-row";
  } else if (row.status === "异常") {
    return "error-row";
  }
  return "warning-row";
};
onMounted(() => {
  setData();
});

const handleTrain = async () => {
  dialogVisible.value = false;
  console.log(trainModelForm);
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
    setData();
  } else {
    ElMessage.error("失败");
  }
};

const handleViewTrainProgress = () => {
  window.open("http://127.0.0.1:5555");
};

const handleOpenDrawer = () => {};

const handleCloseDrawer = () => {};

const handleView = async (row) => {
  modelDetailDrawer.value = true;
  console.log(row);
  modelDetailDrawerData.value = await getModelInfoById(row.key).then((res) => {
    if (res.code === 200) {
      return res.data;
    }
  });
  console.log(modelDetailDrawerData.value);
};

watch(
  () => form,
  () => {
    setData();
  },
  { deep: true },
);
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

  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form" class="demo-form-inline">
      <el-form-item label="包含">
        <el-input
          style="width: 270px"
          v-model="form.include"
          placeholder="请输入include关键字"
        ></el-input>
      </el-form-item>
      <el-form-item label="排除">
        <el-input
          style="width: 270px"
          v-model="form.exclude"
          placeholder="请输入exclude关键字"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" :set-data="setData" />
      </el-form-item>
    </el-form>
  </div>
  <!-- 数据展示 -->
  <h1 style="text-align: center; font-size: 24px; font-weight: 600">
    {{ form.include }}模型管理
  </h1>
  <el-table :data="data" border style="width: 100%">
    <el-table-column prop="_id" label="ID" align="center" />
    <el-table-column prop="key" label="测点编号" align="center" />
    <el-table-column prop="path" label="测点" align="center" />
    <el-table-column prop="model_name" label="模型名称" align="center" />
    <el-table-column prop="time" label="时间" align="center" width="150" />
    <el-table-column prop="current_status" label="当前状态" align="center" />
    <el-table-column prop="train_model_file" label="训练模型" align="center" />
    <el-table-column prop="train_args" label="训练参数" align="center" />
    <el-table-column
      prop="predict_model_file"
      label="预测模型"
      align="center"
    />
    <el-table-column prop="predict_args" label="预测参数" align="center" />
    <el-table-column
      prop="model_train_stderr"
      label="训练错误"
      align="center"
    />
    <el-table-column label="操作" align="center" width="160">
      <template #default="scope">
        <el-button
          type="danger"
          @click="handleOpenTrainModelDialog(scope.row.key)"
          >训练</el-button
        >
        <el-button @click="handleView(scope.row)">查看</el-button>
      </template>
    </el-table-column>
  </el-table>

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
</template>

<style scoped lang="scss">
.input_box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.el-input {
  width: 300px;
  margin-right: 15px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
}

.el-select {
  width: 300px;
}

span {
  display: flex;
  font-size: 16px;
}
</style>
