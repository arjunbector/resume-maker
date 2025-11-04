import OptimizeHandler from "./optimize-handler";

export default function Optimize() {
  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Optimizing</h2>
        <p className="text-muted-foreground text-sm">
          Set back while we optimize your details
        </p>
        <OptimizeHandler />
      </div>
    </div>
  );
}
