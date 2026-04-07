import GastosPanel from "@/src/components/gastosPanel"
import MenuPanel from "@/src/components/menuPanel"

export default function GastosPage() {
  return (
    <>
      <MenuPanel />
      <main style={{ paddingTop: "var(--nav-height, 64px)" }}>
        <GastosPanel />
      </main>
    </>
  )
}