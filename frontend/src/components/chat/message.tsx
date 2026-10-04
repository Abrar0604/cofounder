import * as React from "react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

let mermaidLib: any = null;

function MermaidDiagram({ chart }: { chart: string }) {
  const [svg, setSvg] = React.useState<string>("");
  const id = React.useId().replace(/:/g, "");

  React.useEffect(() => {
    let mounted = true;
    const renderChart = async () => {
      try {
        if (!mermaidLib) {
          mermaidLib = (await import("mermaid")).default;
          mermaidLib.initialize({
            startOnLoad: false,
            theme: "base",
            themeVariables: {
              primaryColor: "#ffffff",
              primaryTextColor: "#000000",
              primaryBorderColor: "#000000",
              lineColor: "#000000",
              secondaryColor: "#f4f4f5",
              tertiaryColor: "#ffffff",
              fontFamily: "inherit",
              background: "#ffffff",
            }
          });
        }
        const { svg: renderedSvg } = await mermaidLib.render(`mermaid-${id}`, chart);
        if (mounted) setSvg(renderedSvg);
      } catch (err) {
        console.error("Mermaid rendering error", err);
        if (mounted) setSvg(`<div class="text-red-500 border border-black p-2 bg-white">Failed to render diagram</div>`);
      }
    };
    renderChart();
    return () => { mounted = false; };
  }, [chart, id]);

  return (
    <div 
      className="my-4 border border-black p-4 bg-white flex justify-center items-center overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

export interface MessageProps {
  id: string;
  role: "user" | "assistant";
  content: string;
  isCompleted?: boolean;
}

export function Message({ role, content }: MessageProps) {
  const isUser = role === "user";
  
  return (
    <div className={cn("flex w-full gap-4 py-4", isUser ? "flex-row-reverse" : "flex-row")}>
      <Avatar className="h-8 w-8 rounded-none border border-black shrink-0">
        {isUser ? (
          <AvatarFallback className="rounded-none bg-black text-white">U</AvatarFallback>
        ) : (
          <AvatarFallback className="rounded-none bg-white text-black">AI</AvatarFallback>
        )}
      </Avatar>
      <div className={cn("flex flex-col gap-2 w-full", isUser ? "items-end" : "items-start")}>
        <div className={cn(
          "px-4 py-2 text-sm max-w-[100%] overflow-hidden",
          isUser ? "bg-black text-white" : "bg-gray-100 text-black border border-gray-200"
        )}>
          <div className="prose prose-sm dark:prose-invert max-w-none break-words overflow-hidden">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code(props: any) {
                const { children, className, node, ...rest } = props
                const match = /language-(\w+)/.exec(className || "")
                if (match && match[1] === "mermaid") {
                  return <MermaidDiagram chart={String(children).replace(/\n$/, "")} />;
                }
                return (
                  <code className={cn("bg-black/10 px-1 py-0.5 font-mono text-xs", className)} {...rest}>
                    {children}
                  </code>
                );
              },
              p({ children }) {
                return <p className="mb-2 last:mb-0 leading-relaxed whitespace-pre-wrap">{children}</p>;
              },
              ul({ children }) {
                return <ul className="list-disc pl-4 mb-2">{children}</ul>;
              },
              ol({ children }) {
                return <ol className="list-decimal pl-4 mb-2">{children}</ol>;
              },
              li({ children }) {
                return <li className="mb-1">{children}</li>;
              },
              h1({ children }) {
                return <h1 className="text-lg font-bold mb-2">{children}</h1>;
              },
              h2({ children }) {
                return <h2 className="text-md font-bold mb-2">{children}</h2>;
              },
              h3({ children }) {
                return <h3 className="text-sm font-bold mb-2">{children}</h3>;
              },
              a({ href, children }) {
                return <a href={href} className="underline" target="_blank" rel="noreferrer">{children}</a>;
              }
            }}
          >
            {content}
          </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  )
}
