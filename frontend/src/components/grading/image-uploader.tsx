import type { RefObject } from "react";
import { Upload, Camera, ImageIcon, X } from "lucide-react";

interface ImageUploaderProps {
  uploadedFile: File | null;
  previewUrl: string | null;
  isProcessing: boolean;
  fileInputRef: RefObject<HTMLInputElement | null>;
  cameraInputRef: RefObject<HTMLInputElement | null>;
  onFileSelected: (file: File) => void;
  onClear: () => void;
}

export function ImageUploader({
  uploadedFile,
  previewUrl,
  isProcessing,
  fileInputRef,
  cameraInputRef,
  onFileSelected,
  onClear,
}: ImageUploaderProps) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">Student Answer Sheet</label>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
        }}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
        }}
      />

      {!uploadedFile ? (
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/20 py-6 transition-colors hover:border-emerald-400/50 hover:bg-emerald-50/30"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100">
              <Upload className="size-5 text-emerald-600" />
            </div>
            <div className="text-center">
              <p className="text-xs font-medium">Upload Image</p>
              <p className="text-[10px] text-muted-foreground">PNG, JPG, PDF</p>
            </div>
          </button>
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/20 py-6 transition-colors hover:border-teal-400/50 hover:bg-teal-50/30"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100">
              <Camera className="size-5 text-teal-600" />
            </div>
            <div className="text-center">
              <p className="text-xs font-medium">Take Photo</p>
              <p className="text-[10px] text-muted-foreground">Use camera</p>
            </div>
          </button>
        </div>
      ) : (
        <div className="relative rounded-lg border bg-muted/20 p-2">
          <button
            onClick={onClear}
            disabled={isProcessing}
            className="absolute -right-2 -top-2 z-10 flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-red-600 shadow-sm hover:bg-red-200 transition-colors disabled:opacity-50"
          >
            <X className="size-3.5" />
          </button>
          {previewUrl && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={previewUrl}
              alt="Uploaded answer"
              className="mx-auto max-h-36 rounded-md object-contain"
            />
          )}
          <p className="mt-2 text-center text-xs text-muted-foreground truncate flex items-center justify-center gap-1.5">
            <ImageIcon className="size-3" />
            {uploadedFile.name}
          </p>
        </div>
      )}
    </div>
  );
}
