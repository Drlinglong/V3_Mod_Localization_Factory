import React from 'react';
import { useTranslation } from 'react-i18next';
import { Modal, TextInput, Button, Group, Stack } from '@mantine/core';
import { useForm } from '@mantine/form';

/**
 * 新建词典文件模态框
 */
const NewFileModal = ({ opened, onClose, onSubmit, isLoading }) => {
    const { t } = useTranslation();

    const form = useForm({
        initialValues: { fileName: '' },
        validate: {
            fileName: (value) => {
                if (!value) return t('glossary_filename_required');
                if (!/^[a-zA-Z0-9_]+\.json$/.test(value)) {
                    return t('glossary_filename_invalid');
                }
                return null;
            }
        }
    });

    const handleSubmit = async (values) => {
        const success = await onSubmit(values.fileName);
        if (success) {
            form.reset();
            onClose();
        }
    };

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title={t('glossary_create_new_file')}
            centered
        >
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack>
                    <TextInput
                        label={t('glossary_filename')}
                        placeholder="example.json"
                        required
                        {...form.getInputProps('fileName')}
                    />
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={onClose}>
                            {t('button_cancel')}
                        </Button>
                        <Button type="submit" loading={isLoading}>
                            {t('button_create')}
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
};

export default NewFileModal;
