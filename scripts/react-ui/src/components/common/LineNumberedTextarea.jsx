import React, { useRef, useEffect, useState } from 'react';
import { Textarea } from '@mantine/core';

export function LineNumberedTextarea({ value, onChange, readOnly, placeholder, scrollRef, onScroll, ...props }) {
    const [lineCount, setLineCount] = useState(1);
    const lineNumbersRef = useRef(null);
    const textareaRef = useRef(null);

    useEffect(() => {
        if (value) {
            const lines = value.split('\n').length;
            setLineCount(lines);
        } else {
            setLineCount(1);
        }
    }, [value]);

    const handleScroll = (e) => {
        if (lineNumbersRef.current) {
            lineNumbersRef.current.scrollTop = e.target.scrollTop;
        }
        if (onScroll) {
            onScroll(e);
        }
    };

    // Sync external ref if provided
    useEffect(() => {
        if (scrollRef) {
            if (typeof scrollRef === 'function') {
                scrollRef(textareaRef.current);
            } else {
                scrollRef.current = textareaRef.current;
            }
        }
    }, [scrollRef]);

    return (
        <div style={{ display: 'flex', height: '100%', border: '1px solid var(--glass-border)', borderRadius: '4px', overflow: 'hidden' }}>
            {/* Line Numbers */}
            <div
                ref={lineNumbersRef}
                style={{
                    width: '40px',
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    color: '#666',
                    textAlign: 'right',
                    padding: '8px 4px',
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    lineHeight: '1.55', // Match Mantine Textarea line-height
                    overflow: 'hidden',
                    userSelect: 'none',
                    borderRight: '1px solid var(--glass-border)'
                }}
            >
                {Array.from({ length: lineCount }, (_, i) => (
                    <div key={i + 1}>{i + 1}</div>
                ))}
            </div>

            {/* Text Area */}
            <Textarea
                ref={textareaRef}
                value={value}
                onChange={onChange}
                readOnly={readOnly}
                placeholder={placeholder}
                onScroll={handleScroll}
                styles={{
                    root: { flex: 1, display: 'flex', flexDirection: 'column' },
                    wrapper: { flex: 1, display: 'flex', flexDirection: 'column' },
                    input: {
                        flex: 1,
                        fontFamily: 'monospace',
                        whiteSpace: 'pre',
                        overflow: 'auto',
                        backgroundColor: readOnly ? 'rgba(0,0,0,0.2)' : undefined,
                        fontSize: '13px',
                        padding: '8px',
                        lineHeight: '1.55',
                        border: 'none',
                        resize: 'none',
                        borderRadius: 0
                    }
                }}
                {...props}
            />
        </div>
    );
}
