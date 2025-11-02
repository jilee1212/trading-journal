'use client';

import { useState, useRef } from 'react';
import { Upload, FileCheck, AlertCircle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
      setError('Only CSV and Excel files are supported');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setSuccess(`Successfully processed ${result.trades_processed} trades!`);
      onUploadSuccess();

      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center gap-4">
        <label
          htmlFor="file-upload"
          className={`
            flex items-center gap-2 px-6 py-3 rounded-lg font-medium cursor-pointer
            transition-all
            ${uploading
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
          `}
        >
          <Upload className="w-5 h-5" />
          {uploading ? 'Uploading...' : 'Upload CSV/Excel'}
        </label>
        <input
          ref={fileInputRef}
          id="file-upload"
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          disabled={uploading}
          className="hidden"
        />
      </div>

      {/* Success Message */}
      {success && (
        <div className="mt-4 flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
          <FileCheck className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-800">{success}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
}
