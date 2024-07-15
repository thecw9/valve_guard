<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount, provide } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";
import { formatNumber } from "@/utils";

const data = ref([]);
const form = reactive({
  station: "韶山站",
  hall: "极1低",
  channel: "通道0",
});

const setData = async () => {
  await getMeasuresInfo(
    form.station + "&" + form.hall + "&" + form.channel + "&" + "声音",
  ).then((res) => {
    if (res.code === 200) {
      // console.log(res.data);
      data.value = res.data
        .map((item) => {
          return {
            key: item.key,
            path: item.path,
            // path: item.path.split("/")[item.path.split("/").length - 1],
            time: item.timestamp.replace("T", " ").split(".")[0],
            value: formatNumber(item.value, 5),
            unit: item.unit,
          };
        })
        .sort((a, b) => {
          return a.key - b.key;
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

let interval = null;
onMounted(() => {
  setData();
  interval = setInterval(() => {
    setData();
  }, 10000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<template>
  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form">
      <el-form-item label="站点">
        <el-select
          v-model="form.station"
          placeholder="请选择站点"
          clearable
          style="width: 270px"
        >
          <el-option label="韶山站" value="韶山站" />
        </el-select>
      </el-form-item>
      <el-form-item label="阀厅">
        <el-select
          v-model="form.hall"
          placeholder="请选择阀厅"
          clearable
          style="width: 270px"
        >
          <el-option label="极1低" value="极1低" />
        </el-select>
      </el-form-item>
      <el-form-item label="通道">
        <el-select
          v-model="form.channel"
          placeholder="请选择通道"
          clearable
          style="width: 270px"
        >
          <el-option label="通道0" value="通道0" />
          <el-option label="通道1" value="通道1" />
          <el-option label="通道2" value="通道2" />
          <el-option label="通道3" value="通道3" />
          <el-option label="通道4" value="通道4" />
          <el-option label="通道5" value="通道5" />
          <el-option label="通道6" value="通道6" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" @set-data="setData" />
      </el-form-item>
    </el-form>
  </div>
  <!-- 数据展示 -->
  <DataTable
    :title="`${form.station} ${form.hall} ${form.channel}声纹在线监测数据`"
    :data="data"
    @set-data="setData"
  />
</template>

<style scoped></style>
