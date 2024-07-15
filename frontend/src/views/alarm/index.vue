<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { getMeasureHistoryAlarm } from "@/api/alarm";
import DataTable from "@/components/DataTable.vue";

const data = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const setData = async () => {
  const start_time = "2019-08-22T14:15:22Z";
  const end_time = new Date();
  const res = await getMeasureHistoryAlarm(
    start_time,
    end_time,
    currentPage.value,
    pageSize.value,
  );
  if (res.code === 200) {
    data.value = res.data.map((item) => {
      return {
        key: item.key,
        path: item.name,
        // path: item.path.split("_")[item.path.split("_").length - 1],
        time: item.service_time?.replace("T", " ").split(".")[0],
        service_time: item.service_time?.replace("T", " ").split(".")[0],
        value: item.value,
        unit: item.unit,
        status:
          item.status === 0
            ? "未知"
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
    total.value = res.total;
  }
};
const handleCurrentChange = (val) => {
  currentPage.value = val;
  setData();
};

let interval = null;
onMounted(() => {
  setData();
  interval = setInterval(() => {
    setData();
  }, 30000);
});

onBeforeUnmount(() => {
  clearInterval(interval);
});
</script>

<template>
  <div class="">
    <div class="table-box">
    <DataTable
      :data="data"
      :title="告警历史"
      @set-data="setData"
    />
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          background
          :total="total"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="prev, pager, next, sizes"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
