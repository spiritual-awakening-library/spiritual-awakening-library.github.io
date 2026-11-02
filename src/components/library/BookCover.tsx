import Image from "next/image";

/**
 * Displays the original book cover spread without cropping or other
 * alteration of its visual content.
 */
export function BookCover({
  src,
  alt,
  width,
  height,
  priority = false,
  sizes = "(min-width: 768px) 560px, 92vw",
  className = "",
}: {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  sizes?: string;
  className?: string;
}) {
  return (
    <div
      className={`overflow-hidden rounded-md border border-line bg-paper-deep ${className}`}
    >
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        sizes={sizes}
        className="h-auto w-full object-contain"
      />
    </div>
  );
}
