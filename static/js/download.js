// script.js
function updateFormFields() {
    const category = document.getElementById('categorySelect').value;
    const studentFields = document.getElementById('studentFields');
    const teacherFields = document.getElementById('teacherFields');

    // 重置所有字段
    studentFields.style.display = 'none';
    teacherFields.style.display = 'none';
    document.getElementById('studentName').removeAttribute('required');
    document.getElementById('studentId').removeAttribute('required');
    document.getElementById('teacherName').removeAttribute('required');
    document.getElementById('teacherId').removeAttribute('required');

    // 根据分类设置必填字段
    if (['开题资料', '中期资料', '答辩资料', '学位论文'].includes(category)) {
        studentFields.style.display = 'block';
        document.getElementById('studentName').setAttribute('required', '');
        document.getElementById('studentId').setAttribute('required', '');
    } else if (category === '专利资料') {
        teacherFields.style.display = 'block';
        document.getElementById('teacherName').setAttribute('required', '');
        document.getElementById('teacherId').setAttribute('required', '');
    }
}

// 表单提交验证
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    const category = document.getElementById('categorySelect').value;

    // 验证分类相关字段
    if (['开题资料', '中期资料', '答辩资料', '学位论文'].includes(category)) {
        if (!document.getElementById('studentName').value || !document.getElementById('studentId').value) {
            alert('请填写姓名和学号');
            e.preventDefault();
            return false;
        }
    } else if (category === '专利资料') {
        if (!document.getElementById('teacherName').value || !document.getElementById('teacherId').value) {
            alert('请填写姓名和工号');
            e.preventDefault();
            return false;
        }
    }

    // 验证文件类型是否选择
    if (!document.getElementById('fileType').value) {
        alert('请选择文件类型');
        e.preventDefault();
        return false;
    }

    return true;
});