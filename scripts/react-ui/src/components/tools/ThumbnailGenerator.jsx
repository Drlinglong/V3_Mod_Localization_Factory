import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Stage, Layer, Rect, Image as KonvaImage, Transformer, Text as KonvaText } from 'react-konva';
import { Button } from 'antd';
import { v4 as uuidv4 } from 'uuid';
import html2canvas from 'html2canvas';

import './ThumbnailGenerator.css';

import flagCn from '../../assets/flags/cn.svg';
import flagUs from '../../assets/flags/us.svg';
import flagJp from '../../assets/flags/jp.svg';
import flagDe from '../../assets/flags/de.svg';

const flagSvgs = {
    cn: flagCn,
    us: flagUs,
    jp: flagJp,
    de: flagDe,
};
const AVAILABLE_FLAGS = [
    { code: 'cn', name: '简体中文' },
    { code: 'us', name: 'English' },
    { code: 'jp', name: '日本語' },
    { code: 'de', name: 'Deutsch' },
];

const AVAILABLE_FONTS = ['Arial', 'Verdana', 'Times New Roman', 'Courier New', 'Georgia', 'Comic Sans MS'];


const DraggableItem = ({ itemProps, isSelected, onSelect, onChange }) => {
    const shapeRef = useRef();
    const trRef = useRef();

    useEffect(() => {
      if (isSelected) {
        trRef.current.nodes([shapeRef.current]);
        trRef.current.getLayer().batchDraw();
      }
    }, [isSelected]);

    const commonProps = {
      onClick: onSelect,
      onTap: onSelect,
      ref: shapeRef,
      draggable: true,
      onDragEnd: (e) => {
        onChange({ ...itemProps, x: e.target.x(), y: e.target.y() });
      },
      onTransformEnd: () => {
        const node = shapeRef.current;
        const scaleX = node.scaleX();
        const scaleY = node.scaleY();
        node.scaleX(1);
        node.scaleY(1);
        onChange({
          ...itemProps,
          x: node.x(),
          y: node.y(),
          width: Math.max(5, node.width() * scaleX),
          height: itemProps.type === 'text' ? 'auto' : Math.max(node.height() * scaleY),
          fontSize: itemProps.type === 'text' ? Math.max(5, (itemProps.fontSize || 20) * scaleY) : itemProps.fontSize,
        });
      },
    };

    return (
      <>
        {itemProps.type === 'image' && <KonvaImage {...commonProps} {...itemProps} />}
        {itemProps.type === 'text' && (
          <KonvaText
            {...commonProps}
            {...itemProps}
            // special handling for text resizing
            onTransform={() => {
                const node = shapeRef.current;
                const scaleX = node.scaleX();
                const scaleY = node.scaleY();
                node.scaleX(1);
                node.scaleY(1);
                onChange({
                  ...itemProps,
                  width: Math.max(5, node.width() * scaleX),
                  height: 'auto',
                  fontSize: Math.max(5, (itemProps.fontSize || 20) * scaleY),
                });
            }}
          />
        )}
        {isSelected && (
          <Transformer
            ref={trRef}
            boundBoxFunc={(oldBox, newBox) => {
              if (newBox.width < 5 || newBox.height < 5) return oldBox;
              return newBox;
            }}
          />
        )}
      </>
    );
};

const ThumbnailGenerator = () => {
    const { t } = useTranslation();
    const canvasContainerRef = useRef(null);
    const [backgroundColor, setBackgroundColor] = useState('#ffffff');
    const [backgroundImage, setBackgroundImage] = useState(null);
    const [elements, setElements] = useState([]);
    const [selectedId, selectShape] = useState(null);

    const handleBgColorChange = (e) => setBackgroundColor(e.target.value);

    const handleBackgroundImageUpload = (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = () => {
                const img = new window.Image();
                img.src = reader.result;
                img.onload = () => {
                    setBackgroundImage(img);
                };
            };
            reader.readAsDataURL(file);
            e.target.value = null;
        }
    };

    const addElement = (newElement) => {
      setElements((prev) => [...prev, newElement]);
    };

    const handleImageUpload = (e, isModImage = false) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = () => {
                const img = new window.Image();
                img.src = reader.result;
                img.onload = () => {
                    const maxWidth = isModImage ? 512 : 128;
                    const maxHeight = isModImage ? 512 : 128;
                    let { width, height } = img;
                    if (width > height) {
                        if (width > maxWidth) {
                            height *= maxWidth / width;
                            width = maxWidth;
                        }
                    } else if (height > maxHeight) {
                        width *= maxHeight / height;
                        height = maxHeight;
                    }

                    const newImage = {
                        type: 'image',
                        image: img,
                        x: isModImage ? (512 - width) / 2 : 50,
                        y: isModImage ? (512 - height) / 2 : 50,
                        width,
                        height,
                        id: uuidv4(),
                    };
                    if (isModImage) {
                        setElements(prev => [newImage, ...prev.filter(el => el.isModImage !== true)]);
                    } else {
                        addElement(newImage);
                    }
                };
            };
            reader.readAsDataURL(file);
            e.target.value = null;
        }
    };

    const handleAddFlag = (code) => {
      const img = new window.Image();
      img.src = flagSvgs[code];
      img.onload = () => {
        addElement({
            type: 'image',
            image: img,
            x: 60,
            y: 60,
            width: 100,
            height: 75,
            id: uuidv4(),
        });
      };
    };

    const handleAddText = () => {
        addElement({
            type: 'text',
            text: t('thumbnail_generator.default_text'),
            x: 70,
            y: 70,
            fontSize: 30,
            fontFamily: 'Arial',
            fill: '#000000',
            id: uuidv4(),
        });
    };

    const checkDeselect = (e) => {
      const clickedOnEmpty = e.target === e.target.getStage();
      if (clickedOnEmpty) selectShape(null);
    };

    const updateElement = (id, newAttrs) => {
        setElements(elements.map(el => (el.id === id ? newAttrs : el)));
    };

    const handleDeleteElement = () => {
        if (selectedId) {
            setElements(elements.filter(el => el.id !== selectedId));
            selectShape(null); // Deselect after deleting
        }
    };

    const handleExport = () => {
        const originallySelectedId = selectedId;
        selectShape(null); // Deselect to hide transformers

        setTimeout(() => {
            if (canvasContainerRef.current) {
                html2canvas(canvasContainerRef.current, {
                    backgroundColor: null,
                    logging: false,
                    useCORS: true,
                }).then(canvas => {
                    const link = document.createElement('a');
                    link.download = 'thumbnail.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    selectShape(originallySelectedId); // Reselect
                });
            } else {
                selectShape(originallySelectedId); // Reselect if ref is null
            }
        }, 100);
    };

    const selectedElement = elements.find(el => el.id === selectedId);

    return (
      <div className="thumbnail-generator-layout">
        <div className="toolbox-panel">
          <h2>{t('thumbnail_generator.toolbox_title')}</h2>
          <div className="tool-section">
            <label htmlFor="mod-image-upload" className="ant-btn">
              {t('thumbnail_generator.upload_mod_image')}
            </label>
            <input id="mod-image-upload" type="file" accept="image/*" onChange={(e) => handleImageUpload(e, true)} style={{ display: 'none' }} />
          </div>
          <div className="tool-section">
            <h4>{t('thumbnail_generator.add_flags')}</h4>
            <div className="flag-list">
              {AVAILABLE_FLAGS.map(({ code, name }) => (
                <img key={code} src={flagSvgs[code]} alt={name} title={name} onClick={() => handleAddFlag(code)} className="flag-item" />
              ))}
            </div>
          </div>
          <div className="tool-section">
              <Button onClick={handleAddText}>{t('thumbnail_generator.add_text')}</Button>
          </div>
        </div>
        <div className="canvas-panel">
          <div id="thumbnail-canvas" ref={canvasContainerRef}>
            <Stage width={512} height={512} onMouseDown={checkDeselect} onTouchStart={checkDeselect}>
              <Layer>
                <Rect width={512} height={512} fill={backgroundColor} />
                {backgroundImage && <KonvaImage image={backgroundImage} width={512} height={512} />}
                {elements.map((item) => (
                   <DraggableItem
                      key={item.id}
                      itemProps={item}
                      isSelected={item.id === selectedId}
                      onSelect={() => selectShape(item.id)}
                      onChange={(newAttrs) => updateElement(item.id, newAttrs)}
                    />
                ))}
              </Layer>
            </Stage>
          </div>
          <Button type="primary" onClick={handleExport} style={{ marginTop: '16px' }}>
            {t('thumbnail_generator.download_thumbnail')}
          </Button>
        </div>
        <div className="inspector-panel">
          <h2>{t('thumbnail_generator.inspector_title')}</h2>
          <div className="tool-section">
            <h4>{t('thumbnail_generator.background_options')}</h4>
            <label>
              {t('thumbnail_generator.background_color')}:&nbsp;
              <input type="color" value={backgroundColor} onChange={handleBgColorChange} />
            </label>
            <label htmlFor="bg-image-upload" className="ant-btn" style={{marginTop: '8px'}}>
                {t('thumbnail_generator.upload_background_image')}
            </label>
            <input id="bg-image-upload" type="file" accept="image/*" onChange={handleBackgroundImageUpload} style={{ display: 'none' }} />
          </div>
          {selectedElement && (
            <div className="tool-section">
                <h4>{t('thumbnail_generator.element_properties')}</h4>
                {selectedElement.type === 'text' && (
                    <div className="property-group">
                        <label>{t('thumbnail_generator.prop_text_content')}</label>
                        <input
                            type="text"
                            className="prop-input"
                            value={selectedElement.text}
                            onChange={(e) => updateElement(selectedId, { ...selectedElement, text: e.target.value })}
                        />
                         <label>{t('thumbnail_generator.prop_font_size')}</label>
                        <input
                            type="number"
                            className="prop-input"
                            value={selectedElement.fontSize}
                            onChange={(e) => updateElement(selectedId, { ...selectedElement, fontSize: Number(e.target.value) })}
                        />
                        <label>{t('thumbnail_generator.prop_font_family')}</label>
                        <select
                            className="prop-input"
                            value={selectedElement.fontFamily}
                            onChange={(e) => updateElement(selectedId, { ...selectedElement, fontFamily: e.target.value })}
                        >
                            {AVAILABLE_FONTS.map(font => <option key={font} value={font}>{font}</option>)}
                        </select>
                         <label>{t('thumbnail_generator.prop_color')}</label>
                         <input
                            type="color"
                            value={selectedElement.fill}
                            onChange={(e) => updateElement(selectedId, { ...selectedElement, fill: e.target.value })}
                        />
                    </div>
                )}
                 {selectedElement.type === 'image' && (
                    <div className="property-group">
                        <label>{t('thumbnail_generator.prop_width')}: {Math.round(selectedElement.width)}px</label>
                        <label>{t('thumbnail_generator.prop_height')}: {Math.round(selectedElement.height)}px</label>
                    </div>
                )}
                <Button danger onClick={handleDeleteElement} style={{ marginTop: '16px' }}>{t('thumbnail_generator.delete_element')}</Button>
            </div>
          )}
        </div>
      </div>
    );
};

export default ThumbnailGenerator;
