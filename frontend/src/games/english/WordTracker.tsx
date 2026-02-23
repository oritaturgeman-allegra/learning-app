/**
 * WordTracker — FAB + Drawer showing all vocabulary words as chips.
 *
 * Both desktop and mobile: FAB button in bottom-left opens a Drawer.
 * Desktop gets a slightly wider drawer for more breathing room.
 */

import { useState } from "react";
import { Box, Chip, Drawer, Fab, Typography, useMediaQuery } from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import type { VocabWord } from "@/data/english";

interface WordTrackerProps {
  vocabulary: VocabWord[];
  practicedWords: Set<string>;
}

export default function WordTracker({ vocabulary, practicedWords }: WordTrackerProps) {
  const isDesktop = useMediaQuery("(min-width:1100px)");
  const [drawerOpen, setDrawerOpen] = useState(false);

  const sorted = [...vocabulary].sort((a, b) => a.english.localeCompare(b.english));
  const remaining = vocabulary.length - practicedWords.size;

  return (
    <>
      <Fab
        size="small"
        onClick={() => setDrawerOpen(true)}
        sx={{
          position: "fixed",
          left: 16,
          bottom: 16,
          zIndex: 10,
          bgcolor: "#c4b5fd",
          color: "white",
          "&:hover": { bgcolor: "#a78bfa" },
        }}
      >
        <MenuBookIcon />
      </Fab>
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: {
            background: "linear-gradient(180deg, #f5f0ff, #fce4ec)",
            pt: 2,
          },
        }}
      >
        <Box
          sx={{
            p: 2,
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
            width: isDesktop ? 320 : 280,
          }}
        >
          <Typography
            sx={{
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              fontSize: "0.95rem",
              textAlign: "center",
              color: "text.secondary",
            }}
          >
            {remaining}/{vocabulary.length} מילים נשארו לתרגל
          </Typography>

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.75, justifyContent: "center" }}>
            {sorted.map((word) => {
              const isPracticed = practicedWords.has(word.english.toLowerCase());
              return (
                <Chip
                  key={word.english}
                  label={word.english}
                  size="small"
                  sx={{
                    fontFamily: "'Fredoka', sans-serif",
                    fontWeight: 500,
                    fontSize: "0.8rem",
                    ...(isPracticed
                      ? {
                          bgcolor: "#99f6e4",
                          color: "#0d9488",
                          textDecoration: "line-through",
                          animation: "chipDone 0.4s ease-out",
                        }
                      : {
                          bgcolor: "rgba(196,181,253,0.3)",
                          color: "#7c3aed",
                        }),
                  }}
                />
              );
            })}
          </Box>
        </Box>
      </Drawer>
    </>
  );
}
