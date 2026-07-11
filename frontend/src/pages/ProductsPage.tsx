export function ProductsPage() {
  return (
    <section className="p-8">
      <div className="rounded-2xl border border-slate-800 bg-[#0b0f17] p-6">
        <p className="text-sm font-medium uppercase tracking-wider text-cyan-400">
          Склад
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Товары
        </h1>

        <p className="mt-3 text-slate-400">
          Здесь будут добавление, редактирование, архивация
          и восстановление товаров.
        </p>
      </div>
    </section>
  )
}