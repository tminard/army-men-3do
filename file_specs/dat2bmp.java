/*
	Army Men 2
	OBJECTS*.DAT Extractor
	May 27, 2014
	herbert3000
*/

import java.io.*;
import java.util.*;

public class dat2bmp {
	
	public static int readByte(RandomAccessFile in) throws IOException {
		return in.readUnsignedByte();
	}
	
	public static int readShort(RandomAccessFile in) throws IOException {
		return readByte(in) | readByte(in) << 8;
	}
	
	public static int readInt(RandomAccessFile in) throws IOException {
		return readByte(in)
			 | readByte(in) << 8
			 | readByte(in) << 16
			 | readByte(in) << 24;
	}
	
	public static void main (String [] args) throws IOException {
		
		String filenames[] = {
			"OBJECTS.DAT",
			"OBJECTS_1.DAT",
			"OBJECTS_2.DAT",
			"OBJECTS_3.DAT",
			"OBJECTS_4.DAT",
			"OBJECTS_5.DAT",
			"OBJECTS_6.DAT",
			"OBJECTS_7.DAT",
			"OBJECTS_8.DAT",
			"OBJECTS_9.DAT",
			"OBJECTS_10.DAT",
			"OBJECTS_11.DAT",
			"OBJECTS_12.DAT",
			"OBJECTS_13.DAT",
			"OBJECTS_14.DAT",
			"OBJECTS_15.DAT"
		};
		
		for (int y=0; y<filenames.length; y++) {
		
		String filename = filenames[y];
		
		RandomAccessFile in = new RandomAccessFile(filename, "r");
		
		in.skipBytes(4); // checksum?
		
		byte pal[] = new byte[0x400];
		in.read(pal);
		
		byte pal_shadow[] = new byte[0x400];
		pal_shadow[0] = pal[0];
		pal_shadow[1] = pal[1];
		pal_shadow[2] = pal[2];
		pal_shadow[252] = 0;
		pal_shadow[253] = 0;
		pal_shadow[254] = 0;
		
		int num_sprites = readInt(in);
		
		int sprite_data[][] = new int[num_sprites][4];
		
		for (int i=0; i<num_sprites; i++) {
			sprite_data[i][0] = readInt(in); // encoded category and type number
			sprite_data[i][1] = (sprite_data[i][0] & 0x7F8000) >> 15;
			sprite_data[i][2] = (sprite_data[i][0] & 0x1FE0) >> 5;
			sprite_data[i][3] = readInt(in); // sprite offset
		}
		
		for (int z=0; z<num_sprites; z++) {
		
			in.seek(sprite_data[z][3]);
			
			int header[] = new int[8];
			header[0] = readShort(in);
			header[1] = readShort(in);
			header[2] = readInt(in);
			header[3] = readInt(in);
			header[4] = readInt(in);
			header[5] = readShort(in);
			header[6] = readShort(in);
			header[7] = readInt(in);
			
			System.out.println(filename+"\t"+z+"\t"+
			                   sprite_data[z][0]+"\tCategory:"+sprite_data[z][1]+"\tNumber:"+
							   sprite_data[z][2]+"\tOffset to sprite: "+sprite_data[z][3]+"\t"+
							   header[0]+"\t"+header[1]+"\t"+header[2]+"\t"+
							   header[3]+"\t"+header[4]+"\t"+header[5]+"\t"+
							   header[6]+"\t"+header[7]);
			
			// section 0
			
			int size   = readInt(in);
			int width  = readShort(in);
			int height = readShort(in);
			
			System.out.println("Offset tbl:\t"+header[4]);
			if (header[4] == 72 || header[4] == 8) {
				in.skipBytes(height*2); // line offset table
			} else if (header[4] == 4 || header[4] == 36 || header[4] == 100 || header[4] == 68) {
				in.skipBytes(height*4); // line offset table
		        } else if (header[4] == 104) {
				in.skipBytes(height*2);
			} else if (header[4] == 32) {
				System.out.println("Offset 32... unknown");
				continue;
			} else if (header[4] == 0) {
				System.out.println("Zero offset");
				height = header[2];
				width = header[3];
				in.skipBytes(12);
				continue;
				// continue; // I think we should seek back 2 pos, then read this as a non RLE image?
			} else {
				System.out.println("Unknown offset, skipping height*2:\t\t"+header[4]);
				in.skipBytes(height*2);
			}
			
			int spaces = (4 - width % 4) % 4;
			int width_ms = width+spaces;

			byte bitmap[] = new byte[height*width_ms];

			if (header[4] == 0) {
				System.out.println("Non RLE... reading " + height*width_ms+" bytes");

				in.read(bitmap);
			} else {
				for (int h=height-1; h>=0; h--) {
					int index=0;
					while (index < width) {
						int t = readByte(in);
						for (int i=0; i<t; i++) {
							bitmap[h*width_ms+index+i] = 0;
						}
						index+=t;

						int p = readByte(in);
						for (int i=0; i<p; i++) {
							bitmap[h*width_ms+index+i] = in.readByte();
						}
						index+=p;
					}
				}
			}

			
			int size_data  = height*width_ms;
			int size_total = size_data + 0x436;
			
			byte bmp_header[] = new byte[0x36];
			bmp_header[0] = 0x42;
			bmp_header[1] = 0x4D;
			bmp_header[2] = (byte)(size_total);
			bmp_header[3] = (byte)(size_total >> 8);
			bmp_header[4] = (byte)(size_total >> 16);
			bmp_header[10] = 0x36;
			bmp_header[11] = 4;
			bmp_header[14] = 0x28;
			bmp_header[18] = (byte)width;
			bmp_header[19] = (byte)(width >> 8);
			bmp_header[22] = (byte)height;
			bmp_header[23] = (byte)(height >> 8);
			bmp_header[26] = 1;
			bmp_header[28] = 8;
			bmp_header[34] = (byte)(size_data);
			bmp_header[35] = (byte)(size_data >> 8);
			bmp_header[36] = (byte)(size_data >> 16);
			
			OutputStream out = new BufferedOutputStream(new FileOutputStream(new File("des\\"+sprite_data[z][1]+"_"+sprite_data[z][2]+"_"+z+".A.bmp")));
			out.write(bmp_header);
			out.write(pal);
			out.write(bitmap);
			out.close();
			
			
			// section 1
			
			size   = readInt(in);
			if (size != 0) {
				width  = readShort(in);
				height = readShort(in);
				
				spaces = (4 - width % 4) % 4;
				width_ms = width+spaces;
				
				in.skipBytes(height*2); // line offset table
				
				bitmap = new byte[height*width_ms];
				
				for (int h=height-1; h>=0; h--) {
					int index=0;
					while (index < width) {
						int t = readByte(in);
						for (int i=0; i<t; i++) {
							bitmap[h*width_ms+index+i] = 0;
						}
						index+=t;
						
						int p = readByte(in);
						for (int i=0; i<p; i++) {
							bitmap[h*width_ms+index+i] = (byte) 0xFF;
						}
						index+=p;
						
						if (index == width-1) {
							bitmap[h*width_ms+index] = 0;
							index++;
						}
					}
				}
				
				size_data  = height*width_ms;
				size_total = size_data + 0x436;
				
				bmp_header = new byte[0x36];
				bmp_header[0] = 0x42;
				bmp_header[1] = 0x4D;
				bmp_header[2] = (byte)(size_total);
				bmp_header[3] = (byte)(size_total >> 8);
				bmp_header[4] = (byte)(size_total >> 16);
				bmp_header[10] = 0x36;
				bmp_header[11] = 4;
				bmp_header[14] = 0x28;
				bmp_header[18] = (byte)width;
				bmp_header[19] = (byte)(width >> 8);
				bmp_header[22] = (byte)height;
				bmp_header[23] = (byte)(height >> 8);
				bmp_header[26] = 1;
				bmp_header[28] = 8;
				bmp_header[34] = (byte)(size_data);
				bmp_header[35] = (byte)(size_data >> 8);
				bmp_header[36] = (byte)(size_data >> 16);
				
				out = new BufferedOutputStream(new FileOutputStream(new File(filename+"_"+z+".B.bmp")));
				out.write(bmp_header);
				out.write(pal_shadow);
				out.write(bitmap);
				out.close();
			}
			
			// section 2
			size   = readInt(in);
			if (size != 0) {
				
				bitmap = new byte[size];
				in.read(bitmap);
				
				size_total = size + 0x3E;
				height+=0x7FFFFFFF;
				
				bmp_header = new byte[0x3E];
				bmp_header[0] = 0x42;
				bmp_header[1] = 0x4D;
				bmp_header[2] = (byte)(size_total);
				bmp_header[3] = (byte)(size_total >> 8);
				bmp_header[4] = (byte)(size_total >> 16);
				bmp_header[10] = 0x3E;
				bmp_header[14] = 0x28;
				bmp_header[18] = (byte)width;
				bmp_header[19] = (byte)(width >> 8);
				bmp_header[22] = (byte)(0xFF-height);
				bmp_header[23] = (byte)(0xFF-(height >> 8));
				bmp_header[24] = (byte)0xFF;
				bmp_header[25] = (byte)0xFF;
				bmp_header[26] = 1;
				bmp_header[28] = 1;
				bmp_header[34] = (byte)(size);
				bmp_header[35] = (byte)(size >> 8);
				bmp_header[36] = (byte)(size >> 16);
				bmp_header[58] = (byte)0xFF;
				bmp_header[59] = (byte)0xFF;
				bmp_header[60] = (byte)0xFF;
				
				out = new BufferedOutputStream(new FileOutputStream(new File(filename+"_"+z+".C.bmp")));
				out.write(bmp_header);
				out.write(bitmap);
				out.close();
			}
			
			//in.skipBytes(16);
			
		} // end for (int z=0; z<num_sprites; z++)
		
		in.close();
		
		} // end (int y=0; y<filenames.length; y++)
		
	 }
}

// ferdinand.graf.zeppelin@gmail.com
