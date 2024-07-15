<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const form = reactive({
  include: "潇江Ⅰ线",
  exclude: "",
});

const setData = async () => {
  await getMeasuresInfo(
    form.include.replace(" ", "&"),
    form.exclude.replace(" ", "&"),
  ).then((res) => {
    if (res.code === 200) {
      data.value = res.data.map((item) => {
        return {
          key: item.key,
          path: item.path,
          // time: item.time.replace("T", " ").split(".")[0],
          time: item.service_time?.replace("T", " ").split(".")[0],
          service_time: item.service_time?.replace("T", " ").split(".")[0],
          value: item.value,
          unit: item.unit,
          status:
            item.status === 0
              ? "模型未训练"
              : item.status === 1
                ? "正常"
                : item.status === 2
                  ? "预警"
                  : item.status === 3
                    ? "报警"
                    : "未知",
          model_name: item.model_name,
          model_is_trained: item.model_is_trained,
          model_updated_at: item.model_updated_at
            ?.replace("T", " ")
            .split(".")[0],
          model_version: item.model_version,
          train_data_total: item.train_data_total,
        };
      });
    }
  });
};

watch(
  () => form,
  () => {
    setData();
  },
  { deep: true },
);

onMounted(() => {
  setData();
});
</script>

<template>
  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form" class="demo-form-inline">
      <el-form-item label="包含">
        <el-input
          v-model="form.include"
          placeholder="请输入include关键字"
        ></el-input>
      </el-form-item>
      <el-form-item label="排除">
        <el-input
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
  <DataTable
    :data="data"
    :title="`${form.include}数据展示`"
    @set-data="setData"
  />
</template>

<style scoped></style>
