import VModal from "./VModal";
import VButton from "./VButton";
import { useTranslation } from "react-i18next";

interface VConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  variant?: "destructive" | "primary";
  isLoading?: boolean;
}

const VConfirmDialog = ({
  isOpen, onClose, onConfirm, title, message,
  confirmText, variant = "destructive", isLoading
}: VConfirmDialogProps) => {
  const { t } = useTranslation();

  return (
    <VModal isOpen={isOpen} onClose={onClose} title={title} className="max-w-sm">
      <p className="text-sm text-muted-foreground mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <VButton variant="ghost" onClick={onClose}>{t("common.cancel")}</VButton>
        <VButton variant={variant} onClick={onConfirm} isLoading={isLoading}>{confirmText ?? t("common.confirm")}</VButton>
      </div>
    </VModal>
  );
};

export default VConfirmDialog;
