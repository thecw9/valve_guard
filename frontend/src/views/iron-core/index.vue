<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";

const data = ref([]);
const form = reactive({
  device: "1000kV潇江Ⅰ线高抗",
});

const setData = async () => {
  await getMeasuresInfo(form.device + "&" + "接地" + "&" + "电流").then(
    (res) => {
      if (res.code === 200) {
        // console.log(res.data);
        data.value = res.data
          .map((item) => {
            return {
              key: item.key,
              path: item.path.includes("高抗")
                ? item.path.split("_")[item.path.split("_").length - 1]
                : item.path.split("_").slice(-2).join("_"),

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
          })
          // .filter((item) => {
          //   return item.unit;
          // })
          .sort((a, b) => {
            return a.key - b.key;
          });
      }
    },
  );
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
  }, 1000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<template>
  <!-- 搜索框 -->
  <div class="input_box">
    <el-form :inline="true" :model="form">
      <el-form-item label="设备">
        <el-select
          v-model="form.device"
          placeholder="请选择设备"
          clearable
          style="width: 270px"
        >
          <el-option label="1000kV潇江Ⅰ线高抗" value="1000kV潇江Ⅰ线高抗" />
          <el-option label="1000kV潇江Ⅱ线高抗" value="1000kV潇江Ⅱ线高抗" />
          <el-option label="1000kV荆潇Ⅰ线高抗" value="1000kV荆潇Ⅰ线高抗" />
          <el-option label="1000kV荆潇Ⅱ线高抗" value="1000kV荆潇Ⅱ线高抗" />
          <el-option label="#2主变" value="#2主变" />
          <el-option label="#3主变" value="#3主变" />
        </el-select>
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
    :title="`${form.device}铁芯夹件在线监测数据`"
    @set-data="setData"
  />
</template>

<style scoped></style>
