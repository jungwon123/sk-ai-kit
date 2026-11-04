export const metadata = { title: "대시보드" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 24, color: "#1d2433" }}>{children}</body>
    </html>
  );
}
