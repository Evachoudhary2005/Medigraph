import "./globals.css";
import Header from "@/components/Header";
import AuthBootstrap from "@/components/AuthBootstrap";

export const metadata = { title: "MediGraph" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <AuthBootstrap />
        <Header />
        {children}
      </body>
    </html>
  );
}