<script setup>
import { ref, reactive, onMounted, watch, onBeforeUnmount, provide } from "vue";
import { getMeasuresInfo } from "@/api/measures";
import DataTable from "@/components/DataTable.vue";
import TrainAllButton from "@/components/TrainAllButton.vue";
import { formatNumber } from "@/utils";

const form = reactive({
  station: "韶山站",
  hall: "极1低",
});
const spectrogram_urls = ref([]);

const updateSpectrogramURL = async () => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - 2); // 2分钟前
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hour = String(now.getHours()).padStart(2, "0");
  const minute = String(now.getMinutes()).padStart(2, "0");

  const baseUrl = "/minio-api/valve-guard/waveform";

  spectrogram_urls.value = [];
  for (let i = 0; i < 7; i++) {
    const url = `${baseUrl}/${year}-${month}-${day}/${hour}-${minute}_ch${i}.png`;
    spectrogram_urls.value.push({
      name: `通道${i}：${year}年${month}月${day}日 ${hour}时${minute}分
    `,
      url: url,
    });
  }
  console.log(spectrogram_urls.value);
};

watch(
  () => form,
  () => {
    updateSpectrogramURL();
  },
  { deep: true },
);

let interval = null;
onMounted(() => {
  updateSpectrogramURL();
  interval = setInterval(() => {
    updateSpectrogramURL();
  }, 1000 * 60);
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
      <el-form-item>
        <el-button type="primary" @click="setData">更新数据</el-button>
        <TrainAllButton :data="data" @set-data="setData" />
      </el-form-item>
    </el-form>
  </div>
  <!-- 频谱展示 -->
  <div class="spectrogram">
    <el-row gutter="20">
      <el-col
        v-for="item in spectrogram_urls"
        :key="item.name"
        :span="12"
        style="margin-bottom: 30px"
      >
        <span style="font-size: 20px; display: flex; justify-content: center">{{
          item.name
        }}</span>
        <el-image
          style="width: 100%; height: 100%"
          :src="item.url"
          fit="contain"
        ></el-image>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped></style>
