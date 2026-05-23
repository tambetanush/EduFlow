import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
}

interface VTableProps<T> {
  columns: Column<T>[];
  data: T[];
  className?: string;
  emptyText?: string;
}

function VTable<T extends Record<string, any>>({ columns, data, className, emptyText = "No records found." }: VTableProps<T>) {
  return (
    <div className={cn("vidya-card overflow-hidden", className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              {columns.map((col) => (
                <th key={col.key} className="vidya-table-header px-6 py-3 text-left">
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-10 text-center text-sm text-muted-foreground">
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((row, i) => (
                <tr key={i} className="border-b border-border last:border-0 hover:bg-accent/50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.key} className="px-6 py-4 text-foreground">
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default VTable;