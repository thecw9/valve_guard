<template>
  <el-form :model="form" class="dynamic-params">
    <el-form-item
      v-for="(param, index) in form.params"
      :key="index"
      class="dynamic-param-item"
    >
      <el-input v-model="param.key" placeholder="Key" class="param-input" />
      <el-input v-model="param.value" placeholder="Value" class="param-input" />
      <el-button type="danger" @click="removeParam(index)" class="remove-button"
        >Remove</el-button
      >
    </el-form-item>
    <el-button type="primary" @click="addParam">Add Parameter</el-button>
    <el-button type="success" @click="submitParams">Submit</el-button>
  </el-form>
</template>

<script>
import { ref } from "vue";
import { ElForm, ElFormItem, ElInput, ElButton } from "element-plus";

export default {
  components: {
    ElForm,
    ElFormItem,
    ElInput,
    ElButton,
  },
  setup() {
    const form = ref({
      params: [{ key: "hfdsaf", value: "test" }],
    });

    const addParam = () => {
      form.value.params.push({ key: "", value: "" });
    };

    const removeParam = (index) => {
      form.value.params.splice(index, 1);
    };

    const submitParams = () => {
      console.log("Submitted Params:", form.value.params);
      console.log(form.value.params);
      // 在这里处理提交逻辑，比如发送到后端
    };

    return {
      form,
      addParam,
      removeParam,
      submitParams,
    };
  },
};
</script>

<style scoped>
.dynamic-params {
  max-width: 600px;
  margin: auto;
}
.dynamic-param-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.param-input {
  flex: 1;
  margin-right: 10px;
}
.remove-button {
  margin-left: 10px;
}
</style>
