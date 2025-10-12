# 指南：维护可伸缩侧边栏与自定义SVG图标系统

本文档旨在说明当前应用中可伸缩侧边栏及自定义SVG图标系统的工作原理，并为未来的开发和维护提供清晰的指引。

---

## 1. 当前实现原理

整个系统由两部分组成：React组件逻辑 和 全局CSS样式。

### a. React组件逻辑 (`scripts/react-ui/src/App.jsx`)

-   **可伸缩行为**:
    -   我们使用Ant Design的 `<Sider>` 组件作为侧边栏容器。
    -   通过React的 `useState` Hook ( `const [collapsed, setCollapsed] = useState(true);` )来管理侧边栏的折叠状态，`true` 为默认折叠。
    -   利用 `<Sider>` 组件的 `onMouseEnter` 和 `onMouseLeave` 事件来触发 `setCollapsed`，实现鼠标悬停时展开 (`false`)，移开时折叠 (`true`) 的效果。

-   **自定义图标集成**:
    -   所有的自定义SVG图标都作为独立的React组件存放在 `scripts/react-ui/src/assets/icons/` 目录下。
    -   在 `App.jsx` 的顶部，我们直接导入这些图标组件（例如 `import HomeIcon from './assets/icons/HomeIcon';`）。
    -   在 `menuItems` 数组中，每个菜单项的 `icon` 属性直接使用这些导入的组件（例如 `icon: <HomeIcon />`），从而替换掉Ant Design的默认图标。

### b. 全局CSS样式 (`scripts/react-ui/src/App.css`)

这是确保图标不变形的关键。经过多次调试，最终的解决方案是以下这段CSS：

```css
/* Final fix for stretched icons, based on runtime DOM analysis */
.ant-menu-item .ant-menu-item-icon {
  font-size: 18px; /* 控制图标的基础尺寸 */
  flex: none;      /* 防止图标作为flex子项被拉伸或压缩，这是关键 */
  width: 1em;      /* 明确设置宽度等于其字体大小 */
  height: 1em;     /* 明确设置高度等于其字体大小 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

-   **为何有效？**
    -   通过运行时DOM分析，我们发现自定义的 `<svg>` 元素在渲染时被Ant Design赋予了 `ant-menu-item-icon` 类。
    -   其父元素 `li.ant-menu-item` 是一个Flex容器。当侧边栏展开时，`li` 变宽，导致其子项（包括图标）被拉伸。
    -   `flex: none;` 这条规则强制图标的尺寸保持固定，**禁止其参与Flex容器的尺寸分配**，从而从根本上解决了拉伸问题。

---

## 2. 如何替换现有图标

替换一个现有图标非常简单，只需两步。假设我们要更新“主页”图标：

1.  **打开图标文件**: 找到并打开 `scripts/react-ui/src/assets/icons/HomeIcon.jsx` 文件。
2.  **替换SVG代码**:
    -   将文件中的 `<svg>...</svg>` 整块代码替换为您新的SVG代码。
    -   **重要**:
        -   确保新的SVG代码也包含 `viewBox="0 0 24 24"` (或其他合适的 `viewBox`)来保证缩放的正确性。
        -   保留 `fill="none"`, `stroke="currentColor"`, `strokeWidth="2"` 等属性，以保持线性、单色的风格统一。
        -   务必保留 `{...props}`，这样组件才能接收并应用Ant Design可能传递的额外属性（如 `className`）。

保存文件后，Vite开发服务器会自动热重载，您无需刷新浏览器即可看到更新后的图标。

---

## 3. 如何为新功能添加图标

为新功能（例如，为未来的“UI Debugger”页面）添加一个新图标，需要三步。

1.  **创建新的图标组件**:
    -   在 `scripts/react-ui/src/assets/icons/` 目录下，创建一个新的 `.jsx` 文件，例如 `UIDebuggerIcon.jsx`。
    -   将您的新SVG代码粘贴进去，并仿照 `HomeIcon.jsx` 的结构，将其包装成一个React组件。确保SVG属性（如 `viewBox`, `stroke` 等）与现有图标保持一致。

    ```jsx
    // scripts/react-ui/src/assets/icons/UIDebuggerIcon.jsx
    import React from 'react';

    const UIDebuggerIcon = (props) => (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        {...props}
      >
        {/* 在这里粘贴您的新SVG路径、圆形等元素 */}
        <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
        <path d="M2 17l10 5 10-5"></path>
        <path d="M2 12l10 5 10-5"></path>
      </svg>
    );

    export default UIDebuggerIcon;
    ```

2.  **在 `App.jsx` 中导入新图标**:
    -   打开 `scripts/react-ui/src/App.jsx`。
    -   在文件顶部的图标导入区域，添加一行来导入您刚创建的组件：

    ```javascript
    import UIDebuggerIcon from './assets/icons/UIDebuggerIcon';
    ```

3.  **在 `menuItems` 中使用新图标**:
    -   在 `App.jsx` 中找到 `menuItems` 数组。
    -   找到或创建一个对应新功能的菜单项，并将其 `icon` 属性设置为 `<UIDebuggerIcon />`。

    ```javascript
    const menuItems = [
        // ... 其他菜单项
        {
            key: '/ui-debugger', // 假设这是新页面的路径
            icon: <UIDebuggerIcon />,
            label: <Link to="/ui-debugger">UI Debugger</Link>,
        },
        // ... 其他菜单项
    ];
    ```

完成以上步骤后，新的菜单项就会带着您设计的全新图标出现在侧边栏中了。
