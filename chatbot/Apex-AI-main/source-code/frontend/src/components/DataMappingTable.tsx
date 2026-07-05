

// Using basic structure representing a TanStack Table for demonstration
export const DataMappingTable = () => {
  const mappings = [
    { sourceColumn: 'DateOfSale', mappedType: 'ISO 8601 Datetime', matchScore: '100%' },
    { sourceColumn: 'StoreNum', mappedType: 'String(64)', matchScore: '98%' },
    { sourceColumn: 'Revenue', mappedType: 'Float', matchScore: '100%' }
  ]

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm mt-6">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 font-medium text-left text-gray-900">Source Column</th>
            <th className="px-4 py-2 font-medium text-left text-gray-900">Mapped Database Type</th>
            <th className="px-4 py-2 font-medium text-left text-gray-900">Confidence Score</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {mappings.map((row, idx) => (
            <tr key={idx}>
              <td className="px-4 py-2 font-medium text-gray-900">{row.sourceColumn}</td>
              <td className="px-4 py-2 text-gray-700">{row.mappedType}</td>
              <td className="px-4 py-2 text-green-600">{row.matchScore}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
