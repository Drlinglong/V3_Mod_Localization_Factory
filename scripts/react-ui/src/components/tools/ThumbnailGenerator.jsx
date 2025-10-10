import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Stage, Layer, Rect, Image as KonvaImage, Transformer, Text as KonvaText } from 'react-konva';
import { Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import html2canvas from 'html2canvas';

import './ThumbnailGenerator.css';

import flagEn from '../../assets/flags/us.svg';
import flagZhCN from '../../assets/flags/cn.svg';
import flagFr from '../../assets/flags/fr.svg';
import flagDe from '../../assets/flags/de.svg';
import flagEs from '../../assets/flags/es.svg';
import flagJa from '../../assets/flags/jp.svg';
import flagKo from '../../assets/flags/ko.svg';
import flagPl from '../../assets/flags/pl.svg';
import flagPtBR from '../../assets/flags/br.svg';
import flagRu from '../../assets/flags/ru.svg';
import flagTr from '../../assets/flags/tr.svg';

const flagSvgs = {
    'en': flagEn,
    'zh-CN': flagZhCN,
    'fr': flagFr,
    'de': flagDe,
    'es': flagEs,
    'ja': flagJa,
    'ko': flagKo,
    'pl': flagPl,
    'pt-BR': flagPtBR,
    'ru': flagRu,
    'tr': flagTr,
};
const AVAILABLE_FLAGS = [
    { "code": "en",    "name": "English" },
    { "code": "zh-CN", "name": "简体中文" },
    { "code": "fr",    "name": "Français" },
    { "code": "de",    "name": "Deutsch" },
    { "code": "es",    "name": "Español" },
    { "code": "ja",    "name": "日本語" },
    { "code": "ko",    "name": "한국어" },
    { "code": "pl",    "name": "Polski" },
    { "code": "pt-BR", "name": "Português do Brasil" },
    { "code": "ru",    "name": "Русский" },
    { "code": "tr",    "name": "Türkçe" }
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

    const itemStyle = isSelected ? {
        shadowColor: 'black',
        shadowBlur: 10,
        shadowOpacity: 0.6,
        shadowOffsetX: 5,
        shadowOffsetY: 5,
    } : {};

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
        {itemProps.type === 'image' && <KonvaImage {...commonProps} {...itemProps} {...itemStyle} />}
        {itemProps.type === 'text' && (
          <KonvaText
            {...commonProps}
            {...itemProps}
            {...itemStyle}
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
            borderStroke="#007bff"
            borderStrokeWidth={2}
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
    const modImageInputRef = useRef(null);
    const bgImageInputRef = useRef(null);
    const customEmblemInputRef = useRef(null);
    const [backgroundColor, setBackgroundColor] = useState('#ffffff');
    const [backgroundImage, setBackgroundImage] = useState(null);
    const [elements, setElements] = useState([]);
    const [selectedId, selectShape] = useState(null);

    const processAndAddEmblem = (file) => {
        const reader = new FileReader();
        reader.onload = () => {
            const img = new window.Image();
            img.src = reader.result;
            img.onload = () => {
                const maxWidth = 128;
                const maxHeight = 128;
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
                    x: 50,
                    y: 50,
                    width,
                    height,
                    id: uuidv4(),
                };
                addElement(newImage);
            };
        };
        reader.readAsDataURL(file);
    };

    const handleCustomEmblemUpload = (e) => {
        if (e.target.files && e.target.files[0]) {
            processAndAddEmblem(e.target.files[0]);
            e.target.value = null;
        }
    };

    const handleBgColorChange = (e) => setBackgroundColor(e.target.value);

    const handleBackgroundImageUpload = (e) => {
        console.log('handleBackgroundImageUpload triggered');
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = () => {
                const img = new window.Image();
                img.src = reader.result;
                img.onload = () => {
                    const canvasWidth = 512;
                    const canvasHeight = 512;
                    let { width, height } = img;

                    const aspectRatio = width / height;
                    const canvasAspectRatio = canvasWidth / canvasHeight;

                    let newWidth = canvasWidth;
                    let newHeight = canvasHeight;

                    if (aspectRatio > canvasAspectRatio) {
                        // Image is wider than canvas, fit by width
                        newHeight = canvasWidth / aspectRatio;
                    } else {
                        // Image is taller than canvas, fit by height
                        newWidth = canvasHeight * aspectRatio;
                    }

                    setBackgroundImage({
                        image: img,
                        x: (canvasWidth - newWidth) / 2,
                        y: (canvasHeight - newHeight) / 2,
                        width: newWidth,
                        height: newHeight,
                    });
                };
            };
            reader.readAsDataURL(file);
            e.target.value = null;
        }
    };

    const addElement = (newElement) => {
      setElements((prev) => [...prev, newElement]);
    };

    const processAndAddImage = (file, isModImage = false) => {
        console.log('processAndAddImage triggered for file:', file.name, 'isModImage:', isModImage);
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
    };

    const handleImageUpload = (e, isModImage = false) => {
        if (e.target.files && e.target.files[0]) {
            processAndAddImage(e.target.files[0], isModImage);
            e.target.value = null;
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        console.log('handleDrop triggered');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type.startsWith('image/')) {
                // Simulate event object for handleBackgroundImageUpload
                handleBackgroundImageUpload({ target: { files: [file] } });
            }
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
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

    const handleAddAllFlags = () => {
        const flagWidth = 80;
        const flagHeight = 60;
        const padding = 10;
        const canvasWidth = 512;
        const canvasHeight = 512;

        const positions = [
            // Left side
            { x: padding, y: padding },
            { x: padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 1 },
            { x: padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 2 },
            { x: padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 3 },
            { x: padding, y: canvasHeight - flagHeight - padding },
            // Right side
            { x: canvasWidth - flagWidth - padding, y: padding },
            { x: canvasWidth - flagWidth - padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 1 },
            { x: canvasWidth - flagWidth - padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 2 },
            { x: canvasWidth - flagWidth - padding, y: padding + (canvasHeight - padding * 2 - flagHeight) / 4 * 3 },
            { x: canvasWidth - flagWidth - padding, y: canvasHeight - flagHeight - padding },
            // Bottom center
            { x: (canvasWidth - flagWidth) / 2, y: canvasHeight - flagHeight - padding },
        ];

        const flagPromises = AVAILABLE_FLAGS.map(flag => {
            return new Promise((resolve) => {
                const img = new window.Image();
                img.src = flagSvgs[flag.code];
                img.onload = () => resolve({img, code: flag.code});
            });
        });

        Promise.all(flagPromises).then(loadedFlags => {
            const newFlagElements = loadedFlags.map((flagData, index) => {
                 // The last flag from app_settings is Turkish, let's put it at the bottom
                if (flagData.code === 'tr') {
                    return {
                        type: 'image',
                        image: flagData.img,
                        x: positions[10].x,
                        y: positions[10].y,
                        width: flagWidth,
                        height: flagHeight,
                        id: uuidv4(),
                    };
                }
                // Distribute the rest
                return {
                    type: 'image',
                    image: flagData.img,
                    x: positions[index].x,
                    y: positions[index].y,
                    width: flagWidth,
                    height: flagHeight,
                    id: uuidv4(),
                };
            }).filter((_, index) => index < positions.length);

            setElements(prev => [...prev, ...newFlagElements]);
        });
    };

    const handleResetCanvas = () => {
        setElements([]);
    };

    const handleDeleteCanvas = () => {
        setBackgroundImage(null);
        setBackgroundColor('#ffffff'); // Reset to default white background
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
    const isCanvasEmpty = !backgroundImage && elements.length === 0;

    return (
      <div className="thumbnail-generator-layout">
        <div className="toolbox-panel">
          <h2>{t('thumbnail_generator.toolbox_title')}</h2>
          <div className="tool-section">
            <Button icon={<UploadOutlined />} onClick={() => modImageInputRef.current && modImageInputRef.current.click()}>
              {t('thumbnail_generator.upload_mod_image')}
            </Button>
            <input ref={modImageInputRef} id="mod-image-upload" type="file" accept="image/*" onChange={(e) => handleImageUpload(e, true)} style={{ display: 'none' }} />
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
              <Button onClick={handleAddText} style={{ marginBottom: '8px' }}>{t('thumbnail_generator.add_text')}</Button>
              <Button onClick={handleAddAllFlags} style={{ marginBottom: '8px' }}>{t('thumbnail_generator.add_all_flags')}</Button>
              <Button danger onClick={handleResetCanvas} style={{ marginBottom: '8px' }}>{t('thumbnail_generator.reset_canvas')}</Button>
              <Button danger onClick={handleDeleteCanvas}>{t('thumbnail_generator.delete_canvas')}</Button>
          </div>
        </div>
        <div className="canvas-panel" onDrop={handleDrop} onDragOver={handleDragOver}>
            {isCanvasEmpty ? (
                <div className="canvas-placeholder" onClick={() => bgImageInputRef.current && bgImageInputRef.current.click()}>
                    <UploadOutlined style={{ fontSize: '48px', color: '#ccc' }} />
                    <p style={{ color: '#aaa', marginTop: '16px' }}>{t('thumbnail_generator.canvas_placeholder')}</p>
                </div>
            ) : (
                <div id="thumbnail-canvas" ref={canvasContainerRef} style={{ width: 512, height: 512 }}>
                    <Stage width={512} height={512} onMouseDown={checkDeselect} onTouchStart={checkDeselect}>
                    <Layer>
                        <Rect width={512} height={512} fill={backgroundColor} />
                        {backgroundImage && <KonvaImage image={backgroundImage.image} x={backgroundImage.x} y={backgroundImage.y} width={backgroundImage.width} height={backgroundImage.height} />}
                        {elements.map((item) => (
                        <DraggableItem
                            key={item.id}
                            itemProps={item}
                            isSelected={item.id === selectedId}
                            onSelect={() => selectShape(item.id === selectedId ? null : item.id)}
                            onChange={(newAttrs) => updateElement(item.id, newAttrs)}
                        />
                        ))}
                    </Layer>
                    </Stage>
                </div>
            )}
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
            <Button icon={<UploadOutlined />} style={{marginTop: '8px'}} onClick={() => bgImageInputRef.current && bgImageInputRef.current.click()}>
                {t('thumbnail_generator.upload_background_image')}
            </Button>
            <input ref={bgImageInputRef} id="bg-image-upload" type="file" accept="image/*" onChange={handleBackgroundImageUpload} style={{ display: 'none' }} />
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
          <div className="tool-section">
            <Button icon={<UploadOutlined />} style={{marginTop: '8px'}} onClick={() => customEmblemInputRef.current && customEmblemInputRef.current.click()}>
              {t('thumbnail_generator.upload_custom_emblem')}
            </Button>
            <input ref={customEmblemInputRef} id="custom-emblem-upload" type="file" accept="image/*" onChange={handleCustomEmblemUpload} style={{ display: 'none' }} />
          </div>
        </div>
      </div>
    );
};

export default ThumbnailGenerator;
