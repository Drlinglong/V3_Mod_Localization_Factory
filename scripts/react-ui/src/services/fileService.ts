// in src/services/fileService.ts

/**
 * 弹出操作系统的文件/文件夹选择对话框。
 * 注意：此功能在浏览器开发环境中是受限的。
 * 我们将使用一个标准的 <input type="file"> 作为临时的、兼容性好的替代方案。
 * 在最终的Tauri/Electron打包版本中，这里将被替换为真正的原生API调用。
 */
export const openProjectDialog = (): Promise<string | null> => {
  return new Promise((resolve) => {
    // 1. 创建一个隐藏的文件输入元素
    const input = document.createElement('input');
    input.type = 'file';
    // 如果需要选择文件夹，可以使用 webkitdirectory 属性
    // input.webkitdirectory = true;

    // 2. 监听它的 change 事件
    input.onchange = (event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        // 在浏览器中，我们只能拿到文件名，拿不到完整路径。
        // 这没关系，我们暂时就用文件名作为占位符。
        const fileName = target.files[0].name;
        console.log(`[Dev Mode] File selected: ${fileName}`);
        resolve(fileName);
      } else {
        resolve(null);
      }
    };

    // 3. 触发它的点击事件，从而弹出浏览器的文件选择框
    input.click();
  });
};
