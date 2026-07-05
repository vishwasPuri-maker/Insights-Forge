import React, { useState } from 'react'
import { UploadCloud } from 'lucide-react'

export const UploadDropzone = () => {
  const [isDragging, setIsDragging] = useState(false)
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    console.log("Files dropped for processing: ", files)
    // Dispatch to FastAPI upload endpoint
  }

  return (
    <div 
      className={`border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center transition-colors ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
      onDragOver={(e: React.DragEvent<HTMLDivElement>) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <UploadCloud className="w-12 h-12 text-gray-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-700">Drag and drop raw telemetry dumps here</h3>
      <p className="text-sm text-gray-500">Supports CSV, XLSX files for autonomous cleaning.</p>
    </div>
  )
}
