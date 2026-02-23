/**
 * HintButton — shared hint popover used by all 4 math games.
 * Shows a lightbulb icon; click opens a popover with Hebrew hint text.
 * Auto-closes after 4 seconds.
 */

import { useEffect, useRef, useState } from "react";
import { IconButton, Popover, Typography } from "@mui/material";
import LightbulbIcon from "@mui/icons-material/Lightbulb";

interface HintButtonProps {
  hint: string | undefined;
}

export default function HintButton({ hint }: HintButtonProps) {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleClick = (e: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(e.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  // Auto-close after 4 seconds
  useEffect(() => {
    if (open) {
      timerRef.current = setTimeout(handleClose, 4000);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [open]);

  if (!hint) return null;

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          color: "#f59e0b",
          bgcolor: "rgba(245, 158, 11, 0.1)",
          "&:hover": { bgcolor: "rgba(245, 158, 11, 0.2)" },
          width: 48,
          height: 48,
        }}
      >
        <LightbulbIcon />
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        transformOrigin={{ vertical: "bottom", horizontal: "center" }}
        slotProps={{
          paper: {
            sx: {
              p: 2,
              maxWidth: 300,
              borderRadius: 3,
              bgcolor: "#fef3c7",
              border: "1px solid #f59e0b",
            },
          },
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontSize: "0.95rem",
            color: "#92400e",
            textAlign: "center",
          }}
        >
          {hint}
        </Typography>
      </Popover>
    </>
  );
}
