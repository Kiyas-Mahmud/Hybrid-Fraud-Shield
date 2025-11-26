export default function Header({ title }: { title: string }) {
  return (
    <div className="sticky top-0 z-50 bg-white px-8 py-6 border-b border-gray-200 shadow-sm">
      <h1 className="text-2xl font-bold text-primary-navy">{title}</h1>
    </div>
  );
}
